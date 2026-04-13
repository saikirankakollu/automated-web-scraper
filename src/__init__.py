"""
Automated Web Scraper Package.

Exposes the main public API for the automated-web-scraper library.
"""

from src.scraper import WebScraper
from src.extractor import DataExtractor
from src.database import DatabaseManager
from src.config_parser import ConfigParser
from src.logger import setup_logger
from src.scheduler import Scheduler

__all__ = [
    "WebScraper",
    "DataExtractor",
    "DatabaseManager",
    "ConfigParser",
    "setup_logger",
    "Scheduler",
]

__version__ = "1.0.0"
