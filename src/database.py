"""Database access layer supporting SQLite and PostgreSQL via SQLAlchemy."""

import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    Integer,
    String,
    Text,
    create_engine,
    text,
)
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from src.logger import setup_logger
from src.utils import ensure_directory

logger = setup_logger(__name__)


class _Base(DeclarativeBase):
    pass


class _Product(_Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(512))
    price = Column(Float)
    brand = Column(String(256))
    url = Column(Text)
    image_url = Column(Text)
    rating = Column(Float)
    stock = Column(String(128))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
    )


class _ScrapeLog(_Base):
    __tablename__ = "scrape_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    domain = Column(String(256), nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    status = Column(String(64), nullable=False)
    records_extracted = Column(Integer, default=0)
    errors = Column(Text)


class DatabaseManager:
    """Persist scraped products and scrape session logs.

    Supports SQLite (default) and PostgreSQL backends through SQLAlchemy.

    Args:
        db_type: ``"sqlite"`` or ``"postgresql"``.
        connection_string: Full SQLAlchemy URL.  When provided *db_type* and
            *db_path* are ignored.
        db_path: Relative or absolute path for the SQLite file.

    Example::

        db = DatabaseManager()
        db.create_tables()
        db.insert_product({"name": "Widget", "price": 9.99, "url": "…"})
        db.close()
    """

    def __init__(
        self,
        db_type: str = "sqlite",
        connection_string: Optional[str] = None,
        db_path: str = "data/scraper.db",
    ) -> None:
        if connection_string:
            url = connection_string
        elif db_type == "sqlite":
            ensure_directory("data")
            url = f"sqlite:///{db_path}"
        elif db_type == "postgresql":
            raise ValueError(
                "Provide a full connection_string for PostgreSQL, e.g. "
                "postgresql+psycopg2://user:pass@host/dbname"
            )
        else:
            raise ValueError(f"Unsupported db_type: '{db_type}'")

        self._engine = create_engine(url, echo=False)
        self._Session = sessionmaker(bind=self._engine)
        logger.info("DatabaseManager connected to %s", url)

    # ------------------------------------------------------------------
    # Schema
    # ------------------------------------------------------------------

    def create_tables(self) -> None:
        """Create the ``products`` and ``scrape_logs`` tables if absent."""
        _Base.metadata.create_all(self._engine)
        logger.info("Database tables ensured.")

    # ------------------------------------------------------------------
    # Products
    # ------------------------------------------------------------------

    def insert_product(self, data: Dict[str, Any]) -> int:
        """Insert a single product record.

        Unknown keys in *data* are silently ignored so that callers can pass
        raw extractor output without pre-filtering.

        Args:
            data: Mapping of product fields (see :class:`_Product` for schema).

        Returns:
            The auto-assigned primary key of the new row.
        """
        allowed = {c.key for c in _Product.__table__.columns} - {"id"}
        row = _Product(**{k: v for k, v in data.items() if k in allowed})
        with self._Session() as session:
            session.add(row)
            session.commit()
            session.refresh(row)
            product_id: int = row.id
        logger.debug("Inserted product id=%s name=%s", product_id, data.get("name"))
        return product_id

    def insert_products_batch(self, products_list: List[Dict[str, Any]]) -> int:
        """Insert multiple product records in a single transaction.

        Args:
            products_list: List of product dicts.

        Returns:
            Number of records inserted.
        """
        if not products_list:
            return 0
        allowed = {c.key for c in _Product.__table__.columns} - {"id"}
        rows = [
            _Product(**{k: v for k, v in p.items() if k in allowed})
            for p in products_list
        ]
        with self._Session() as session:
            session.add_all(rows)
            session.commit()
        logger.info("Batch inserted %d products.", len(rows))
        return len(rows)

    def get_products(
        self,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Query the products table.

        Args:
            filters: Optional ``{column: value}`` equality filters.
            limit: Maximum number of rows to return.

        Returns:
            List of dicts, one per matching product row.
        """
        with self._Session() as session:
            query = session.query(_Product)
            if filters:
                for col, val in filters.items():
                    if hasattr(_Product, col):
                        query = query.filter(getattr(_Product, col) == val)
            rows = query.limit(limit).all()
        return [
            {c.key: getattr(r, c.key) for c in _Product.__table__.columns}
            for r in rows
        ]

    # ------------------------------------------------------------------
    # Scrape logs
    # ------------------------------------------------------------------

    def log_scrape(
        self,
        domain: str,
        status: str,
        records_extracted: int = 0,
        errors: Optional[str] = None,
    ) -> int:
        """Record a scrape session in the ``scrape_logs`` table.

        Args:
            domain: The domain or scraper name being logged.
            status: Outcome string such as ``"success"`` or ``"failed"``.
            records_extracted: Count of successfully extracted records.
            errors: Optional error message or traceback string.

        Returns:
            The auto-assigned primary key of the new log row.
        """
        row = _ScrapeLog(
            domain=domain,
            status=status,
            records_extracted=records_extracted,
            errors=errors,
        )
        with self._Session() as session:
            session.add(row)
            session.commit()
            session.refresh(row)
            log_id: int = row.id
        logger.info(
            "Scrape log id=%s domain=%s status=%s records=%d",
            log_id,
            domain,
            status,
            records_extracted,
        )
        return log_id

    def get_scrape_logs(
        self, domain: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Retrieve scrape log entries.

        Args:
            domain: When provided, only return logs for this domain.

        Returns:
            List of log dicts ordered by timestamp descending.
        """
        with self._Session() as session:
            query = session.query(_ScrapeLog)
            if domain:
                query = query.filter(_ScrapeLog.domain == domain)
            rows = query.order_by(_ScrapeLog.timestamp.desc()).all()
        return [
            {c.key: getattr(r, c.key) for c in _ScrapeLog.__table__.columns}
            for r in rows
        ]

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def close(self) -> None:
        """Dispose the SQLAlchemy engine and release all connections."""
        self._engine.dispose()
        logger.info("DatabaseManager connection closed.")
