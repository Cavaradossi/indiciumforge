"""Storage subpackage: relational metadata (SQLite) and time-series (DuckDB/Parquet).

``SQLiteMetadataStore`` has no third-party dependencies. ``ParquetDuckDBMarketDataStore``
is imported lazily-safe (DuckDB/PyArrow are only required when it is *used*), so the
package stays importable without the ``[storage]`` extra installed.
"""

from indiciumforge_core.storage.parquet_duckdb import ParquetDuckDBMarketDataStore
from indiciumforge_core.storage.sqlite_metadata import SQLiteMetadataStore

__all__ = ["ParquetDuckDBMarketDataStore", "SQLiteMetadataStore"]
