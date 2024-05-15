from __future__ import annotations

from typing import TYPE_CHECKING

from libs.webserver.executer_base import ExecuterBase, update
from loguru import logger

if TYPE_CHECKING:
    from libs.webserver.messages import BadRequest, NotFound


class GeneralSettingsExecuter(ExecuterBase):

    def get_general_setting(self, setting_key: str) -> dict | NotFound:
        """Return a specific general setting."""
        return {
            "setting_key": setting_key,
            "setting_value": self._config["general_settings"][setting_key]
        }

    def get_general_settings(self) -> dict[str, dict]:
        """Return all general settings."""
        return {
            "setting_value": self._config["general_settings"]
        }

    def set_general_setting(self, settings: dict) -> dict | NotFound | BadRequest:
        """Set multiple general settings."""
        update(self._config["general_settings"], settings)

        self.save_config()
        self.refresh_device(self.all_devices_id)

        return {
            "settings": settings
        }

    def get_webserver_port(self) -> int:
        """Return the webserver port, 8080 by default."""
        if "webserver_port" in self._config["general_settings"]:
            return self._config["general_settings"]["webserver_port"]
        return 8080

    def reset_settings(self) -> dict:
        """Reset all general settings to default."""
        self._reset_config()
        self.refresh_device(self.all_devices_id)
        return {}

    def _reset_config(self) -> None:
        """Reset the config to default. Internal method."""
        self._config_instance.reset_config()
        self._config = self._config_instance.config

    def import_config(self, imported_config: dict) -> bool:
        """Import a new config and load it."""
        if imported_config is None:
            logger.error("Could not import Config. Config is None.")
            return False

        logger.debug(f"Type of imported config: {type(imported_config)}")
        if isinstance(imported_config, dict):
            self._config = imported_config
            self.save_config()
            self._config_instance.check_compatibility()
            self.refresh_device(self.all_devices_id)
            return True
        logger.error("Unknown Type.")
        return False
