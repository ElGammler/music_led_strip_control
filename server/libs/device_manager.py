import copy
import logging
import sys
from time import time

from libs.color_service_global import ColorServiceGlobal  # pylint: disable=E0611, E0401
from libs.config_service import ConfigService  # pylint: disable=E0611, E0401
from libs.device import Device  # pylint: disable=E0611, E0401
from libs.fps_limiter import FPSLimiter  # pylint: disable=E0611, E0401
from libs.notification_enum import NotificationEnum  # pylint: disable=E0611, E0401
from libs.notification_item import NotificationItem  # pylint: disable=E0611, E0401
from libs.queue_wrapper import QueueWrapper  # pylint: disable=E0611, E0401


class DeviceManager:
    def start(self, config_lock, notification_queue_in, notification_queue_out, effect_queue, audio_queue):
        self.logger = logging.getLogger(__name__)

        self._config_lock = config_lock
        self._config = ConfigService.instance(self._config_lock).config

        self._notification_queue_in = QueueWrapper(notification_queue_in)
        self._notification_queue_out = QueueWrapper(notification_queue_out)
        self._effect_queue = QueueWrapper(effect_queue)
        self._audio_queue = QueueWrapper(audio_queue)

        self._all_devices_ID = "all_devices"

        # Init FPS Limiter.
        self._fps_limiter = FPSLimiter(120)

        self._skip_routine = False
        self._devices = {}
        self.init_devices()
        self.start_devices()

        self.start_time = time()
        self.ten_seconds_counter = time()

        try:
            while True:
                self.routine()
        except KeyboardInterrupt:
            sys.exit()

    def routine(self):
        self.check_effect_changes()
        self.check_config_changes()

        # Limit the fps to decrease lags caused by 100 percent CPU.
        self._fps_limiter.fps_limiter()

        if self._skip_routine:
            return

        audio_data = self.get_audio_data()
        self.refresh_audio_queues(audio_data)

        self.end_time = time()

        if time() - self.ten_seconds_counter > 10:
            self.ten_seconds_counter = time()
            self.time_dif = self.end_time - self.start_time
            self.fps = 1 / self.time_dif
            self.logger.info(f"FPS: {self.fps:.2f}")

        self.start_time = time()

    def check_effect_changes(self):
        # Check the effect queue.
        if not self._effect_queue.empty():
            current_effect_item = self._effect_queue.get_blocking()
            self.logger.debug(
                f"Device Manager received new effect: {current_effect_item.effect_enum} {current_effect_item.device_id}")

            if current_effect_item.device_id == self._all_devices_ID:
                for current_device_id in self._devices:
                    current_device = self._devices[current_device_id]
                    current_device.effect_queue.put_blocking(
                        current_effect_item)
            else:
                current_device = self._devices[current_effect_item.device_id]
                current_device.effect_queue.put_blocking(current_effect_item)

    def check_config_changes(self):
        if not self._notification_queue_in.empty():
            current_notification_item = self._notification_queue_in.get_blocking()
            self.logger.debug(
                f"Device Manager received new notification: {current_notification_item.notification_enum} - {current_notification_item.device_id}")

            if current_notification_item.notification_enum is NotificationEnum.config_refresh:

                devices_count_before_reload = len(
                    self._config["device_configs"].keys())
                self.logger.debug(
                    f"Device count before: {devices_count_before_reload}")
                self.reload_config()
                devices_count_after_reload = len(
                    self._config["device_configs"].keys())
                self.logger.debug(
                    f"Device count after: {devices_count_after_reload}")

                if (devices_count_before_reload != devices_count_after_reload):
                    self.reinit_devices()

                if (current_notification_item.device_id == self._all_devices_ID):
                    for key in self._devices:
                        self.restart_device(key)
                else:
                    self.restart_device(current_notification_item.device_id)
                self._notification_queue_out.put_blocking(NotificationItem(
                    NotificationEnum.config_refresh_finished, current_notification_item.device_id))

            elif current_notification_item.notification_enum is NotificationEnum.process_continue:
                self._skip_routine = False
            elif current_notification_item.notification_enum is NotificationEnum.process_pause:
                self._skip_routine = True

    def get_audio_data(self):
        audio_data = None
        if not self._audio_queue.empty():
            audio_data = self._audio_queue.get_blocking()
        return audio_data

    def refresh_audio_queues(self, audio_data):
        if audio_data is None:
            return
        for value in self._devices.values():
            audio_copy = copy.deepcopy(audio_data)
            value.audio_queue.put_none_blocking(audio_data)

    def init_devices(self):
        self.logger.debug("Entering init_devices()")
        self._color_service_global = ColorServiceGlobal(self._config)

        for key in self._config["device_configs"]:
            device_id = key
            self.logger.debug(f"Init device with device id: {device_id}")
            self._devices[device_id] = Device(
                self._config, self._config["device_configs"][device_id], self._color_service_global)
        self.logger.debug("Leaving init_devices()")

    def reinit_devices(self):
        self.logger.debug("Entering reinit_devices()")
        for key in self._devices:
            self.stop_device(key)
        self._devices = {}
        self.init_devices()
        self.start_devices()
        self.logger.debug("Leaving reinit_devices()")

    def start_devices(self):
        for key, value in self._devices.items():
            self.logger.debug(f"Starting device: {key}")
            try:
                value.start_device()
            except TypeError:
                self.logger.exception(f"Could not start device {key}.")

    def reload_config(self):
        self.logger.debug("Entering reload_config()")
        ConfigService.instance(self._config_lock).load_config()
        self._config = ConfigService.instance(self._config_lock).config
        self.logger.debug("Leaving reload_config()")

    def restart_device(self, device_id):
        self.logger.debug(f"Restarting {device_id}")
        self._devices[device_id].refresh_config(
            self._config, self._config["device_configs"][device_id])
        self.logger.debug(f"Restarted {device_id}")

    def stop_device(self, device_id):
        self.logger.debug(f"Stopping {device_id}")
        self._devices[device_id].stop_device()
        self.logger.debug(f"Stopped {device_id}")
