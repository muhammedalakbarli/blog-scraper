from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Iterable
from pathlib import Path
import logging
import json
import sqlite3
import csv


# ==============================
# Base Exporter Interface
# ==============================

class Exporter(ABC):
    """
    Abstract base exporter.
    Every exporter must implement `export`.
    """

    @abstractmethod
    def export(self, data: List[Dict[str, Any]]) -> None:
        pass


# ==============================
# Validation Mixin
# ==============================

class DataValidationMixin:
    """
    Shared validation logic for exporters.
    """

    REQUIRED_KEYS = {"text", "author", "tags"}

    @classmethod
    def validate(cls, data: List[Dict[str, Any]]) -> None:
        if not isinstance(data, list):
            raise TypeError("Data must be a list of dictionaries.")

        if not data:
            raise ValueError("Cannot export empty dataset.")

        for item in data:
            if not isinstance(item, dict):
                raise TypeError("Each item must be a dictionary.")

            missing = cls.REQUIRED_KEYS - item.keys()
            if missing:
                raise ValueError(f"Missing required keys: {missing}")


# ==============================
# CSV Exporter
# ==============================

class CSVExporter(Exporter, DataValidationMixin):
    """
    Exports structured data into CSV format.
    """

    def __init__(self, filename: str = "posts.csv"):
        self.path = Path(filename)

    def export(self, data: List[Dict[str, Any]]) -> None:
        self.validate(data)

        try:
            keys = data[0].keys()
            with open(self.path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=keys)
                writer.writeheader()
                writer.writerows(data)

            logging.info(f"[CSV] Export successful → {self.path.resolve()}")

        except Exception as e:
            logging.exception("CSV export failed.")
            raise RuntimeError("CSV export failed.") from e


# ==============================
# JSON Exporter
# ==============================

class JSONExporter(Exporter, DataValidationMixin):
    """
    Exports structured data into JSON format.
    """

    def __init__(self, filename: str = "posts.json"):
        self.path = Path(filename)

    def export(self, data: List[Dict[str, Any]]) -> None:
        self.validate(data)

        try:
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)

            logging.info(f"[JSON] Export successful → {self.path.resolve()}")

        except Exception as e:
            logging.exception("JSON export failed.")
            raise RuntimeError("JSON export failed.") from e


# ==============================
# SQLite Exporter
# ==============================

class SQLiteExporter(Exporter, DataValidationMixin):
    """
    Exports data into SQLite database.
    Automatically creates table and prevents duplicates.
    """

    TABLE_NAME = "quotes"

    def __init__(self, db_name: str = "posts.db"):
        self.db_path = Path(db_name)

    def export(self, data: List[Dict[str, Any]]) -> None:
        self.validate(data)

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                self._create_table(cursor)
                self._insert_batch(cursor, data)

                conn.commit()

            logging.info(f"[SQLite] Export successful → {self.db_path.resolve()}")

        except Exception as e:
            logging.exception("SQLite export failed.")
            raise RuntimeError("SQLite export failed.") from e

    def _create_table(self, cursor: sqlite3.Cursor) -> None:
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {self.TABLE_NAME} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT NOT NULL,
                author TEXT NOT NULL,
                tags TEXT,
                UNIQUE(text, author)
            )
        """)

    def _insert_batch(
        self,
        cursor: sqlite3.Cursor,
        data: Iterable[Dict[str, Any]]
    ) -> None:
        cursor.executemany(f"""
            INSERT OR IGNORE INTO {self.TABLE_NAME} (text, author, tags)
            VALUES (:text, :author, :tags)
        """, data)