from __future__ import annotations

from contextlib import contextmanager
import importlib.util
import logging
import os
from pathlib import Path
import platform
import typing as t

import nox

## Set nox options
if importlib.util.find_spec("uv"):
    nox.options.default_venv_backend = "uv|virtualenv"
else:
    nox.options.default_venv_backend = "virtualenv"
nox.options.reuse_existing_virtualenvs = True
nox.options.error_on_external_run = False
nox.options.error_on_missing_interpreters = False
# nox.options.report = True

## Define sessions to run when no session is specified
nox.sessions = ["ruff-lint", "export"]

## Create logger for this module
log: logging.Logger = logging.getLogger("nox")

## Define versions to test
PY_VERSIONS: list[str] = ["3.13", "3.12"]
## Get tuple of Python ver ('maj', 'min', 'mic')
PY_VER_TUPLE: tuple[str, str, str] = platform.python_version_tuple()
## Dynamically set Python version
DEFAULT_PYTHON: str = f"{PY_VER_TUPLE[0]}.{PY_VER_TUPLE[1]}"

# this VENV_DIR constant specifies the name of the dir that the `dev`
# session will create, containing the virtualenv;
# the `resolve()` makes it portable
VENV_DIR = Path("./.venv").resolve()

## Paths to sub-apps with their own uv project
UV_PARENT_DIRS = [
    "collectors/openmeteo-collector/",
    "collectors/weatherapi-collector/",
    "api-server/",
    "shared/",
    "schedulers/temporal-scheduler/",
]


def install_uv_project(
    session: nox.Session, external: bool = False, pip_install: bool = False
) -> None:
    """Method to install uv and the current project in a nox session."""
    log.info("Installing uv in session")
    session.install("uv")
    log.info("Syncing uv project")
    session.run("uv", "sync", external=external)

    if pip_install:
        log.info("Installing project")
        session.run("uv", "pip", "install", ".", external=external)


@contextmanager
def cd(new_dir) -> t.Generator[None, t.Any, None]:  # type: ignore
    """Context manager to change a directory before executing command."""
    prev_dir: str = os.getcwd()
    os.chdir(os.path.expanduser(new_dir))
    try:
        yield
    finally:
        os.chdir(prev_dir)


@nox.session(name="dev-env", tags=["setup"])
def dev(session: nox.Session) -> None:
    """Sets up a python development environment for the project.

    Run this on a fresh clone of the repository to automate building the project with uv.
    """
    ## Install apps
    with cd("shared"):
        log.info("Installing shared/ app")
        install_uv_project(session, external=True, pip_install=False)

    with cd("collectors/weatherapi-collector/"):
        log.info("Installing weatherapi-collector/ app")
        install_uv_project(session, external=True, pip_install=False)

    # with cd("collectors/openmeteo-collector/"):
    #     log.info("Installing openmeteo-collector/ app")
    #     install_uv_project(session, external=True, pip_install=False)

    # with cd("api-server/"):
    #     log.info("Installing api-server/ app")
    #     install_uv_project(session, external=True, pip_install=False)

    ## Setup root project
    install_uv_project(session, external=True)


@nox.session(python=[DEFAULT_PYTHON], name="ruff-lint", tags=["ruff", "clean", "lint"])
def run_linter(session: nox.Session):
    """Nox session to run Ruff code linting."""
    ## Base paths - adjust as necessary: root is current working directory
    root = Path(".").resolve()

    ## Collect workspace member directories:
    #  This will match your uv workspace globs
    members = (
        list(root.glob("collectors/*"))
        + [root / "shared"]
        + [root / "servers/*"]
        + [root / "scripts"]
    )

    session.install("ruff")

    ## Iterate over sub-apps & lint
    for member_path in members:
        if not member_path.exists():
            session.log(f"Skipping non-existent path: {member_path}")
            continue

        session.log(f"Running ruff lint on {member_path}")
        session.run(
            "ruff",
            "check",
            str(member_path),
            "--fix",
            external=True,
        )

    ## Lint noxfile
    session.run(
        "ruff",
        "check",
        "noxfile.py",
        "--fix",
        external=True,
    )


@nox.session(python=[DEFAULT_PYTHON], name="vulture-check", tags=["quality"])
def run_vulture_check(session: nox.Session):
    # exclude_patterns = "*.venv,*/.venv/*,*/__pycache__/*"

    session.install(f"vulture")

    log.info("Checking for dead code with vulture")

    ## shared/
    session.run("vulture", "shared/", "--min-confidence", "100")

    ## collectors/openmeteo-collector/
    session.run("vulture", "collectors/openmeteo-collector/", "--min-confidence", "100")

    ## collectors/weatherapi-collector/
    session.run(
        "vulture", "collectors/weatherapi-collector/", "--min-confidence", "100"
    )

    ## api-server/
    session.run("vulture", "servers/api-server/", "--min-confidence", "100")

    ## Temporal scheduler
    session.run("vulture", "schedulers/temporal-scheduler/", "--min-confidence", "100")

    ## noxfile.py
    session.run("vulture", "noxfile.py", "--min-confidence", "100")

    ## scripts/
    session.run("vulture", "scripts/", "--min-confidence", "100")

    log.info("Finished checking for dead code with vulture")


@nox.session(name="export-requirements")
def export_requirements(session: nox.Session):
    ## List of paths or globs to search for pyproject.toml files
    app_paths = [
        "shared",
        "collectors/*",
        "servers/*",
        "schedulers/*",
    ]

    ## Install uv to run commands
    session.install("uv")

    for pattern in app_paths:
        ## Use glob to find matching app directories containing pyproject.toml
        for app_dir in sorted(Path(".").glob(pattern)):
            pyproject_file = app_dir / "pyproject.toml"

            if pyproject_file.exists():
                session.log(f"Exporting requirements for {app_dir}")

                session.run(
                    "uv",
                    "pip",
                    "compile",
                    str(pyproject_file),
                    "-o",
                    str(app_dir / "requirements.txt"),
                    external=True,
                )
            else:
                session.log(f"No pyproject.toml found in {app_dir}, skipping")


###########
# Alembic #
###########


@nox.session(python=[DEFAULT_PYTHON], name="alembic-migrate", tags=["alembic", "db"])
def run_alembic_migrations(session: nox.Session):
    # session.install("alembic")
    install_uv_project(session)

    log.info("Running database migrations with alembic")

    session.run(
        "alembic", "revision", "--autogenerate", "-m", "'autogenerated migration'"
    )
    session.run("alembic", "upgrade", "head")


@nox.session(python=[DEFAULT_PYTHON], name="alembic-upgrade", tags=["alembic", "db"])
def run_alembic_migrations(session: nox.Session):
    # session.install("alembic")
    install_uv_project(session)

    revision = input("Revision to upgrade (default: 'head'): ") or "head"
    log.info(f"Running alembic upgrade {revision}")

    session.run("alembic", "upgrade", revision)


@nox.session(python=[DEFAULT_PYTHON], name="alembic-init", tags=["init"])
def run_alembic_initialization(session: nox.Session):
    if Path("./database/migrations").exists():
        log.warning(
            "Migrations directory [./database/migrations] exists. Skipping alembic init."
        )
        return

    install_uv_project(session)

    log.info("Initializing Alembic database")

    session.run("alembic", "init", "database/migrations")

    log.info(
        """
!! READ THIS !!

Alembic initialized at path ./database/migrations.

You must edit ./database/migrations/env.py to configure your project.

If you're using a "src" layout, add this to the top of your code:

import sys

sys.path.append("./src")

Import your SQLAlchemy models (look for the commented sections describing model imports),
set your SQLAlchemy Base.metadata, and set the database URI.

If you're using Dynaconf, i.e. in a `db.settings.DB_SETTINGS` object, you can set the
database URI like:

## Get database URI from config
#  !! You have to write this function !!
DB_URI = get_db_uri()
## Set alembic's SQLAlchemy URL
if DB_URI:
    config.set_main_option(
        "sqlalchemy.url", DB_URI.render_as_string(hide_password=False)
    )
else:
    raise Exception("DATABASE_URL not found in Dynaconf settings")
    
!! READ THIS !! 
"""
    )
