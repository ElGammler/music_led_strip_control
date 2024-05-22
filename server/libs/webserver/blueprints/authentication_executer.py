import platform
import re
import secrets
from configparser import ConfigParser, MissingSectionHeaderError, ParsingError
from copy import deepcopy
from pathlib import Path
from typing import TypedDict
from urllib.parse import urljoin, urlparse

from flask import Flask, Response, redirect, request, session, url_for
from flask_login import LoginManager, UserMixin, login_user
from libs.webserver.executer_base import ExecuterBase
from loguru import logger

login_manager = LoginManager()


class PinConfig(TypedDict):
    """Type definition for the PIN config dictionary."""

    DEFAULT_PIN: str
    USE_PIN_LOCK: bool


class User(UserMixin):
    def __init__(self, user_id: str) -> None:
        self.id = user_id


@login_manager.user_loader
def user_loader(user_id: str) -> User:
    if not AuthenticationExecuter.instance.is_pin_active():
        return None
    return User(user_id)


@login_manager.unauthorized_handler
def unauthorized() -> Response:
    # TODO: Do not check amount of url queries, so that an API key can be used.
    # if request.path.startswith("/api/"):
    #     error_msg = {
    #         "error": "Unauthorized",
    #         "message": "No valid API key provided."
    #         "status": 401
    #     }
    #     return jsonify(error_msg), 401
    session["next"] = request.path
    return redirect(url_for("authentication_api.login", next=session.get("next")))


class AuthenticationExecuter(ExecuterBase):
    def __init__(self, config_lock, notification_queue_in, notification_queue_out, effects_queue, py_audio) -> None:
        super().__init__(config_lock, notification_queue_in, notification_queue_out, effects_queue, py_audio)

        AuthenticationExecuter.instance = self

        self.default_values: PinConfig = {
            "DEFAULT_PIN": "",
            "USE_PIN_LOCK": False
        }
        self.config = ConfigParser()
        self.config_path: Path = Path("../security.ini")
        self.config_values = self.read_config()
        self.USER_PIN: str = self.config_values["DEFAULT_PIN"]
        self.IS_PIN_ACTIVE: bool = self.config_values["USE_PIN_LOCK"]

    def add_server_authentication(self, server: Flask) -> Flask:
        logger.debug("Enter add_server_authentication()")

        if not self.validate_pin(self.USER_PIN) and self.IS_PIN_ACTIVE:
            msg = "PIN must be from 4 to 8 digits."
            raise ValueError(msg)

        server.secret_key = secrets.token_urlsafe(16)  # Force login on restart.
        if not self.IS_PIN_ACTIVE:
            # TODO: LOGIN_DISABLED will be deprecated.
            # https://github.com/maxcountryman/flask-login/issues/697
            server.config["LOGIN_DISABLED"] = True
        login_manager.init_app(server)

        return server

    def save_config(self) -> None:
        """Save PIN config to file."""
        logger.debug("Saving PIN to file...")
        with Path.open(self.config_path, "w") as configfile:
            self.config.write(configfile)
            if platform.system().lower() == "linux":
                Path.chmod(self.config_path, 775)
        logger.debug("Pin saved to file.")

    def reset_config(self) -> None:
        """Reset the PIN config file to default values."""
        logger.debug("Resetting PIN...")
        for section in self.config.sections():
            self.config.remove_section(section)
        self.config["SECURITY"] = deepcopy(self.default_values)
        self.save_config()
        logger.debug("PIN reset.")

    def read_config(self) -> PinConfig:
        """Read PIN settings from config file. Check if .ini file exists and if security options are valid."""
        default_values = deepcopy(self.default_values)
        try:
            logger.debug("Reading PIN config...")
            dataset = self.config.read(self.config_path)
            logger.debug("PIN config read.")
        except (ParsingError, MissingSectionHeaderError) as e:
            logger.debug(f"Reading PIN failed: {e}")
            self.reset_config()
            dataset = self.config.read(self.config_path)

        logger.debug(f"PIN config: {self.config}, dataset: {dataset}")

        if self.config_path.as_posix() in dataset:
            try:
                new_values: PinConfig = {
                    "DEFAULT_PIN": self.config["SECURITY"].get("DEFAULT_PIN"),
                    "USE_PIN_LOCK": self.config["SECURITY"].getboolean("USE_PIN_LOCK")
                }
                return new_values
            except (ValueError, KeyError) as e:
                logger.debug(f"PIN dataset failed: {e}")
                self.reset_config()
                return default_values
        else:
            logger.debug("PIN file is not in dataset.")
            self.reset_config()
        logger.debug("PIN read from file.")
        return default_values

    @staticmethod
    def validate_pin(pin: str) -> bool:
        """Validate PIN to be from 4 to 8 digits."""
        return bool(re.fullmatch(r"\d{4,8}", pin))

    @staticmethod
    def is_safe_url(target: str) -> bool:
        """Check if URL is safe to redirect to."""
        ref_url = urlparse(request.host_url)
        test_url = urlparse(urljoin(request.host_url, target))
        return test_url.scheme in {"http", "https"} and ref_url.netloc == test_url.netloc

    def set_pin_setting(self, data: PinConfig) -> None:
        """Interface to set PIN settings from API."""
        logger.debug("Enter set_pin_setting()")
        self.config["SECURITY"] = data
        self.save_config()

    def get_pin_setting(self) -> PinConfig:
        """Interface to get PIN settings from API."""
        logger.debug("Enter get_pin_setting()")
        return self.read_config()

    def reset_pin_settings(self) -> PinConfig:
        """Interface to reset PIN settings from API."""
        logger.debug("Enter reset_pin_settings()")
        self.reset_config()
        return self.read_config()

    @staticmethod
    def login() -> None:
        """Log in the user."""
        logger.debug("Enter login()")
        user_id = "1001"
        user = User(user_id)
        login_user(user)

    def is_pin_active(self) -> bool:
        """Check if PIN is active."""
        logger.debug("Enter is_pin_active()")
        return self.IS_PIN_ACTIVE
