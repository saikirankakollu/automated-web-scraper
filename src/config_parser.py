"""Configuration file parser supporting JSON and YAML formats."""

import json
import os
import re
from typing import Any, Dict, Optional

import yaml

from src.logger import setup_logger

logger = setup_logger(__name__)


class ConfigParser:
    """Load, validate, and manage scraper configuration files.

    Supports JSON and YAML formats with environment variable substitution
    and sensible defaults.

    Example::

        parser = ConfigParser()
        config = parser.load("config/my_site.yaml")
    """

    REQUIRED_FIELDS = ("name", "seed_urls", "extraction")

    def __init__(self) -> None:
        """Initialise ConfigParser with an empty config store."""
        self._config: Dict[str, Any] = {}

    # ------------------------------------------------------------------
    # Loading helpers
    # ------------------------------------------------------------------

    def load_json(self, filepath: str) -> Dict[str, Any]:
        """Load and return configuration from a JSON file.

        Args:
            filepath: Path to the JSON configuration file.

        Returns:
            Parsed configuration dictionary.

        Raises:
            FileNotFoundError: When *filepath* does not exist.
            json.JSONDecodeError: When the file contains invalid JSON.
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Config file not found: {filepath}")
        with open(filepath, "r", encoding="utf-8") as fh:
            config = json.load(fh)
        self._config = self.substitute_env_vars(config)
        logger.info("Loaded JSON config from %s", filepath)
        return self._config

    def load_yaml(self, filepath: str) -> Dict[str, Any]:
        """Load and return configuration from a YAML file.

        Args:
            filepath: Path to the YAML configuration file.

        Returns:
            Parsed configuration dictionary.

        Raises:
            FileNotFoundError: When *filepath* does not exist.
            yaml.YAMLError: When the file contains invalid YAML.
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Config file not found: {filepath}")
        with open(filepath, "r", encoding="utf-8") as fh:
            config = yaml.safe_load(fh)
        self._config = self.substitute_env_vars(config or {})
        logger.info("Loaded YAML config from %s", filepath)
        return self._config

    def load(self, filepath: str) -> Dict[str, Any]:
        """Auto-detect the file format and load the configuration.

        Format detection is based on the file extension (``.json``,
        ``.yaml``, ``.yml``).

        Args:
            filepath: Path to a ``.json``, ``.yaml``, or ``.yml`` file.

        Returns:
            Parsed configuration dictionary.

        Raises:
            ValueError: When the file extension is not recognised.
        """
        ext = os.path.splitext(filepath)[1].lower()
        if ext == ".json":
            return self.load_json(filepath)
        if ext in {".yaml", ".yml"}:
            return self.load_yaml(filepath)
        raise ValueError(
            f"Unsupported config format '{ext}'. Use .json, .yaml, or .yml."
        )

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def validate(self, config: Dict[str, Any]) -> bool:
        """Check that *config* contains all required top-level fields.

        Args:
            config: Configuration dictionary to validate.

        Returns:
            ``True`` if valid.

        Raises:
            ValueError: Listing all missing required fields.
        """
        missing = [f for f in self.REQUIRED_FIELDS if f not in config]
        if missing:
            raise ValueError(
                f"Config is missing required fields: {', '.join(missing)}"
            )
        if not isinstance(config.get("seed_urls"), list) or not config["seed_urls"]:
            raise ValueError("'seed_urls' must be a non-empty list.")
        logger.debug("Config validation passed.")
        return True

    # ------------------------------------------------------------------
    # Defaults
    # ------------------------------------------------------------------

    def get_default_config(self) -> Dict[str, Any]:
        """Return a configuration dictionary with sensible default values.

        Returns:
            Default configuration dict that can be used as a base for
            custom configurations.
        """
        return {
            "name": "default_scraper",
            "seed_urls": [],
            "scraping": {
                "method": "requests",
                "delay": 2,
                "retry_count": 3,
                "timeout": 30,
                "user_agent_rotation": True,
                "proxies": [],
            },
            "extraction": {
                "fields": {},
                "multiple_products": False,
                "product_container": None,
            },
            "pagination": {
                "enabled": False,
                "next_page_selector": None,
                "max_pages": 1,
            },
            "database": {
                "enabled": True,
                "type": "sqlite",
                "path": "data/scraper.db",
            },
            "export": {
                "csv": False,
                "json": False,
                "output_dir": "exports/",
            },
        }

    # ------------------------------------------------------------------
    # Environment variable substitution
    # ------------------------------------------------------------------

    def substitute_env_vars(self, config: Any) -> Any:
        """Recursively replace ``${ENV_VAR}`` placeholders with env values.

        Unset variables are left as-is so that missing configuration is
        surfaced clearly at runtime.

        Args:
            config: Configuration object (dict, list, or scalar).

        Returns:
            Config with placeholders replaced by environment variable values.
        """
        if isinstance(config, dict):
            return {k: self.substitute_env_vars(v) for k, v in config.items()}
        if isinstance(config, list):
            return [self.substitute_env_vars(item) for item in config]
        if isinstance(config, str):
            return re.sub(
                r"\$\{([^}]+)\}",
                lambda m: os.environ.get(m.group(1), m.group(0)),
                config,
            )
        return config
