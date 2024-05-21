#
#   Contains all configuration for the server.
#   Load and save the config after every change.
#
from __future__ import annotations

import json
import sys
from pathlib import Path
from shutil import copy, copyfile

from jsonschema.exceptions import ValidationError
from loguru import logger

from libs.config_converter.config_converter_service import ConfigConverterService  # pylint: disable=E0611, E0401
from libs.webserver.schemas.config_validator_service import ConfigValidatorService  # pylint: disable=E0611, E0401


class ConfigService:
    def __init__(self: ConfigService, config_lock) -> None:
        self.config = None

        # Start with the default logging settings, because the config was not loaded.
        self.setup_logging()

        self.config_validator_service = ConfigValidatorService()

        config_file = Path("config.json")
        config_backup_file = Path("config_backup.json")
        config_template_file = Path("config_template.json")

        rel_config_path = Path("../../.mlsc/")
        # Convert relative path to abs path.
        config_folder = Path(rel_config_path).resolve()
        lib_folder = Path(__file__).parent.resolve()

        self._config_path = config_folder / config_file
        self._backup_path = config_folder / config_backup_file
        self._template_path = lib_folder / config_template_file

        logger.debug("Config Files")
        logger.debug(f"Config: {self._config_path}")
        logger.debug(f"Backup: {self._backup_path}")
        logger.debug(f"Template: {self._template_path}")

        if not Path.exists(self._config_path):
            if not Path.exists(self._backup_path):
                # Use the template as config.
                Path(config_folder).mkdir(exist_ok=True)  # Create config directory, ignore if already exists.
                copyfile(self._template_path, self._config_path)  # Copy config.json from repository to config directory.
            else:
                # Use the backup as template.
                Path(config_folder).mkdir(exist_ok=True)  # Create config directory, ignore if already exists.
                copyfile(self._backup_path, self._config_path)  # Copy config.json from repository to config directory.

        self.config_lock = config_lock

        self.load_config()

        # Now the config was loaded, so we can reinit the logging with the set logging levels.
        self.setup_logging()

    def load_config(self):
        """Load the configuration file inside the self.config variable."""
        self.config_lock.acquire()

        try:
            with Path.open(self._config_path, "r") as read_file:
                self.config = json.load(read_file)
        except Exception as e:
            logger.error(f"Could not load config due to exception: {e}")
            self.load_backup()

        self.config_lock.release()

        logger.debug("Settings loaded from config.")

    def save_config(self, config=None):
        """Save the config file. Use the current self.config."""
        logger.debug("Saving settings...")

        self.config_lock.acquire()

        self.save_backup()

        if config is not None:
            self.config = config

        with Path.open(self._config_path, "w") as write_file:
            json.dump(self.config, write_file, indent=4, sort_keys=True)

        # Maybe the logging updated
        self.setup_logging()
        self.config_lock.release()

    def load_backup(self):
        try:
            with Path.open(self._backup_path, "r") as read_file:
                self.config = json.load(read_file)
        except Exception as e:
            logger.error(f"Could not load backup config due to exception: {e}")

    def save_backup(self):
        copy(self._config_path, self._backup_path)

    def reset_config(self):
        """Reset the config."""
        logger.debug("Resetting config...")

        self.config_lock.acquire()

        config_template = self.load_template()
        if config_template is not None:
            self.config = config_template

        self.config_lock.release()

        # Save the config again.
        self.save_config()

    def load_template(self):
        if not Path.exists(self._template_path):
            error_msg = f'Could not find the template config file: "{self._template_path}"'
            raise FileNotFoundError(error_msg)

        # Read the Backup Config.
        with Path.open(self._template_path, "r") as read_file:
            try:
                return json.load(read_file)
            except json.JSONDecodeError:
                return None

    def check_compatibility(self):
        loaded_config = self.config
        template_config = self.load_template()

        config_converter_service = ConfigConverterService()
        loaded_config = config_converter_service.upgrade(loaded_config)

        # Loop through the root.
        for key in template_config:
            if key == "device_configs":
                continue

            if key not in loaded_config:
                loaded_config[key] = template_config[key]
                continue

            self.check_leaf(loaded_config[key], template_config[key])

        self.check_devices(loaded_config["device_configs"], template_config["default_device"])

        self.config = loaded_config

        # TODO: Figure out how to validate default groups.

        try:
            self.config_validator_service.validate_config(self.config)
        except ValidationError as e:
            # Todo: Handle validation errors.
            # https://python-jsonschema.readthedocs.io/en/stable/errors/
            logger.error(f"Could not validate config settings: {e}")
            # self.load_backup()

        self.save_config()

    def check_leaf(self, loaded_config_leaf, template_config_leaf):
        if type(template_config_leaf) is dict:
            for key, value in template_config_leaf.items():
                if key not in loaded_config_leaf:
                    loaded_config_leaf[key] = value
                    continue

                self.check_leaf(loaded_config_leaf[key], value)

    def check_devices(self, loaded_config_devices, template_config_device):
        for value in loaded_config_devices.values():
            self.check_leaf(value, template_config_device)

    def get_config_path(self):
        return self._config_path

    def setup_logging(self):
        """Set up Loguru logging."""
        # Loguru on Windows (for testing) does not support multiprocessing well because of spawning instead of forking.
        # Loggers inside child processes will ignore any custom configuration like log levels and use the default config.
        logging_path = Path("../../.mlsc/")
        logging_file = Path("mlsc.log")

        format_string_file = "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}"
        format_string_console = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"

        logging_level_map = {
            "notset": "TRACE",
            "debug": "DEBUG",
            "info": "INFO",
            "warning": "WARNING",
            "error": "ERROR",
            "critical": "CRITICAL"
        }

        logging_level_console = "INFO"
        logging_level_file = "INFO"
        logging_file_enabled = False

        if self.config is not None:
            try:
                logging_level_console = logging_level_map[self.config["general_settings"]["log_level_console"]]
                logging_level_file = logging_level_map[self.config["general_settings"]["log_level_file"]]
                logging_file_enabled = self.config["general_settings"]["log_file_enabled"]
            except KeyError as e:
                print(f"Could not load logging settings. Key does not exist: {e}")  # noqa: T201

        if not Path.exists(logging_path):
            Path(logging_path).mkdir(parents=True, exist_ok=True)

        # Clear existing handlers.
        logger.remove()

        # Console handler.
        logger.add(sys.stderr, format=format_string_console, level=logging_level_console, colorize=True, enqueue=True)

        # File handler (if enabled).
        if logging_file_enabled:
            log_file = logging_path / logging_file
            logger.add(log_file, format=format_string_file, level=logging_level_file, rotation="5 MB", retention=5, enqueue=True)

    @staticmethod
    def instance(config_lock, imported_instance=None) -> ConfigService:
        """Return the current instance of the Config_Service.

        Use this method and not the current_instance variable directly.
        This method will create the config if it's null.
        """
        if imported_instance is not None:
            ConfigService.current_instance = imported_instance

        if not hasattr(ConfigService, "current_instance"):
            ConfigService.current_instance = ConfigService(config_lock)

        return ConfigService.current_instance
