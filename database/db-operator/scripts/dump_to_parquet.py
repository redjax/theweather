import sys
import time

from pathlib import Path
from datetime import datetime
from dynaconf import Dynaconf
import pandas as pd
from sqlalchemy import create_engine
import glob
import pyarrow as pa
import pyarrow.parquet as pq

BASE_DIR = Path(__file__).parent

SETTINGS = Dynaconf(
    merge_enabled=True,
    root_path=BASE_DIR,
    settings_files=[
        str(BASE_DIR / "settings.toml"),
        str(BASE_DIR / "settings.local.toml"),
    ],
)

SQLITE_SETTINGS = SETTINGS.get("SQLITE", {})
BACKUP_SETTINGS = SETTINGS.get("BACKUP", {})


def merge_parquet_chunks(output_dir: Path, date_str: str, table: str):
    pattern = f"{date_str}_{table}_part*.parquet"
    files = list(output_dir.glob(pattern))

    if not files:
        print(f"No chunk files found for {table}, skipping merge.")
        return

    tables = [pq.read_table(str(file)) for file in files]
    combined_table = pa.concat_tables(tables)

    merged_path = output_dir / f"{date_str}_{table}.parquet"
    pq.write_table(combined_table, str(merged_path))

    print(f"Merged {len(files)} chunks into {merged_path}")

    for file in files:
        file.unlink()

    print(f"Deleted {len(files)} chunk files for {table}")


start_time = time.time()

## Paths as pathlib.Path objects
sqlite_path = Path(SQLITE_SETTINGS.get("FILE"))
pq_output_dir = Path(BACKUP_SETTINGS.get("pq_output_dir"))

if not sqlite_path:
    raise ValueError("Missing path to SQLite database file")

if not pq_output_dir:
    raise ValueError("Missing path to ")

pq_output_dir.mkdir(parents=True, exist_ok=True)

date_str = datetime.now().strftime("%Y-%m-%d")

## Use string for SQLAlchemy engine url
engine = create_engine(f"sqlite:///{sqlite_path.as_posix()}")

print(f"Getting list of tables from SQLite database")
tables = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table';", engine)[
    "name"
].tolist()

if len(tables) == 0:
    print(f"[WARNING] No tables found in database: {sqlite_path}")
    sys.exit(0)

chunk_size = 10000

print(f"Dumping [{len(tables)}] table(s)")
for table in tables:
    print(f"Processing table: {table}")
    batch_num = 0
    sql_query = f"SELECT * FROM {table}"

    for chunk in pd.read_sql(sql_query, engine, chunksize=chunk_size):
        batch_num += 1
        filename = f"{date_str}_{table}_part{batch_num}.parquet"
        filepath = pq_output_dir / filename

        chunk.to_parquet(filepath, index=False)

        print(f"Exported chunk {batch_num} of table {table} to {filepath}")

    print(f"Merging exported chunks into single .parquet file")
    merge_parquet_chunks(pq_output_dir, date_str, table)

end_time = time.time()
elapsed = end_time - start_time

print(f"All tables processed and merged. Script took [{elapsed}] second(s) to execute")
