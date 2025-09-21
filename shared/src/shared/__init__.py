"""Shared configurations for weather applications.

Description:
    Provides configurations that other applications can fallback to,
    like a shared logging configuration, or shared database settings.

    Applications can (and should) contain their own isolated configurations,
    but can search the shared configuration path for settings.toml and .secrets.toml
    files if no local configuration is found.
"""
