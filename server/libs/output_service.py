import sys
from time import time

import numpy as np
from loguru import logger

from libs.fps_limiter import FPSLimiter
from libs.notification_enum import NotificationEnum
from libs.output_enum import OutputsEnum
from libs.outputs.output_dummy import OutputDummy
from libs.outputs.output_raspi import OutputRaspi
from libs.outputs.output_udp import OutputUDP


class OutputService:
    def start(self, device):

        self._device = device
        self._led_strip = self._device.device_config["led_strip"]

        logger.info(f'Starting Output service... Device: {self._device.device_config["device_name"]}')

        # Initial config load.
        self._config = self._device.config

        self._output_queue = self._device.output_queue
        self._device_notification_queue_in = self._device.device_notification_queue_in
        self._device_notification_queue_out = self._device.device_notification_queue_out

        self.ten_seconds_counter = time()
        self.sec_ten_seconds_counter = time()
        self.start_time = time()

        # Init FPS Limiter.
        self._fps_limiter = FPSLimiter(self._device.device_config["fps"])

        self._skip_output = False
        self._cancel_token = False

        self._available_outputs = {
            OutputsEnum.output_dummy: OutputDummy,
            OutputsEnum.output_raspi: OutputRaspi,
            OutputsEnum.output_udp: OutputUDP
        }

        current_output_enum = OutputsEnum[self._device.device_config["output_type"]]
        logger.debug(f"Found output: {current_output_enum}")
        self._current_output = self._available_outputs[current_output_enum](
            self._device)

        logger.debug(f'Output component started. Device: {self._device.device_config["device_name"]}')

        try:
            while not self._cancel_token:
                self.output_routine()
        except KeyboardInterrupt:
            sys.exit()

    def output_routine(self):
        # Limit the fps to decrease lags caused by 100 percent CPU.
        self._fps_limiter.fps_limiter()

        # Check the notification queue.
        if not self._device_notification_queue_in.empty():
            self._current_notification_in = self._device_notification_queue_in.get_blocking()

        if hasattr(self, "_current_notification_in"):
            if self._current_notification_in is NotificationEnum.config_refresh:
                self.refresh()
            elif self._current_notification_in is NotificationEnum.process_continue:
                self._skip_output = False
            elif self._current_notification_in is NotificationEnum.process_pause:
                self._skip_output = True
            elif self._current_notification_in is NotificationEnum.process_stop:
                self.stop()

        # Reset the current in notification, to do it only one time.
        self._current_notification_in = None

        # Skip the output sequence, for example to "pause" the process.
        if self._skip_output:
            if not self._output_queue.empty():
                skip_output_queue = self._output_queue.get_blocking()
                del skip_output_queue
            return

        # Check if the queue is empty and stop if its empty.
        if not self._output_queue.empty():
            current_output_array = self._output_queue.get_blocking()
            # Add another Array of LEDS for White Channel
            if "sk6812" in self._led_strip and len(current_output_array) == 3:
                current_output_array = np.vstack(
                    (current_output_array, np.zeros(self._device.device_config["led_count"])))

            self._current_output.show(current_output_array)

        self.end_time = time()

        if time() - self.ten_seconds_counter > 10:
            self.ten_seconds_counter = time()
            self.time_dif = self.end_time - self.start_time
            self.fps = 1 / self.time_dif
            logger.info(f'FPS: {self.fps:.2f} | Device: {self._device.device_config["device_name"]}')

        self.start_time = time()

    def stop(self):
        self._cancel_token = True
        self._current_output.clear()

    def refresh(self):
        logger.debug("Refreshing output...")

        # Refresh the config,
        self._config = self._device.config

        # Notify the master component, that I'm finished.
        self._device_notification_queue_out.put_blocking(
            NotificationEnum.config_refresh_finished)

        logger.debug("Output refreshed.")
