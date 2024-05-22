import atexit
from collections.abc import Mapping
from functools import wraps

from apscheduler.schedulers.background import BackgroundScheduler
from jsonschema import Draft202012Validator, ValidationError, validate
from loguru import logger

from libs.config_service import ConfigService
from libs.effect_item import EffectItem
from libs.effects_enum import EffectsEnum
from libs.notification_enum import NotificationEnum
from libs.notification_item import NotificationItem

scheduler = BackgroundScheduler()


def handle_config_errors(func):
    """# WARNING: DEPRECATED.

    Decorator for catching any `Key` or `Value` errors in the config when calling API endpoints.
    In case of error, None is returned.
    """
    @wraps(func)
    def wrapper(*args, **kwargs) -> None:
        try:
            return func(*args, **kwargs)
        except (KeyError, ValueError):
            return None
    return wrapper


def update(orig: dict, new: dict) -> dict:
    """Update a dict recursively with new values.

    Also, overwrite `device_groups` without keeping old values.

    https://stackoverflow.com/questions/3232943.
    """
    for k, v in new.items():
        if k == "device_groups":
            orig[k] = v
        if isinstance(v, Mapping):
            orig[k] = update(orig.get(k, {}), v)
        else:
            orig[k] = v
    return orig


def validate_schema(data: dict, schema: dict) -> bool:
    """Validate the request data against a JSON schema.

    All API schemas are defined in `/libs/webserver/schemas/`.
    """
    try:
        validate(data, schema, format_checker=Draft202012Validator.FORMAT_CHECKER)
    except ValidationError as e:
        path_fmt = " -> ".join([str(p) for p in e.absolute_path])
        logger.error(f"Schema validation error in request:\n{path_fmt} - {e.message}")

        return False

    return True


class ExecuterBase:
    def __init__(self, config_lock, notification_queue_in, notification_queue_out, effects_queue, py_audio) -> None:
        self._config_lock = config_lock
        self.notification_queue_in = notification_queue_in
        self.notification_queue_out = notification_queue_out
        self.effects_queue = effects_queue
        self._py_audio = py_audio

        # Initial config load.
        self._config_instance = ConfigService.instance(self._config_lock)
        self._config = self._config_instance.config

        self.export_config_path = self._config_instance.get_config_path()

        self.all_devices_id = "all_devices"

        self.scheduler = scheduler
        if not self.scheduler.running:
            self.scheduler.start()

        atexit.register(self.shutdown_scheduler)

    def shutdown_scheduler(self):
        if self.scheduler.running:
            self.scheduler.shutdown()

    # Helper
    def save_config(self):
        self._config_instance.save_config(self._config)

    def put_into_effect_queue(self, device, effect):
        logger.debug("Preparing new EnumItem...")
        effect_item = EffectItem(EffectsEnum[effect], device)
        logger.debug(f"EnumItem prepared: {effect_item.effect_enum} {effect_item.device_id}")

        self.effects_queue.put(effect_item)
        logger.debug("EnumItem put into queue.")

    def put_into_notification_queue(self, notificication, device):
        logger.debug("Preparing new Notification...")
        notification_item = NotificationItem(notificication, device)
        logger.debug(f"Notification Item prepared: {notification_item.notification_enum} {notification_item.device_id}")
        self.notification_queue_out.put(notification_item)
        logger.debug("Notification Item put into queue.")

    def refresh_device(self, device_id):
        self.put_into_notification_queue(NotificationEnum.config_refresh, device_id)

    @staticmethod
    def validate_data_in(dictionary: dict, keys: tuple) -> bool:
        """WARNING: DEPRECATED."""
        if not isinstance(dictionary, dict):
            logger.error("Error in validate_data_in: dictionary is not a dict.")
            return False

        if keys is None:
            logger.error("Error in validate_data_in: keys tuple is None.")
            return False

        for currentkey in keys:
            if currentkey not in dictionary:
                logger.error(f"Error in validate_data_in: Could not find the key: {currentkey}")
                logger.error("Dict:")
                logger.error(str(dictionary))
                return False

            if dictionary[currentkey] is None:
                logger.error(f"Error in validate_data_in: dictionary entry is None. Key: {currentkey}")
                logger.error("Dict:")
                logger.error(str(dictionary))
                return False

        return True
