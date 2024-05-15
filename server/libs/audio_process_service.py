import sys
from multiprocessing import Queue
from time import time

import numpy as np
import pyaudio
from loguru import logger

from libs.audio_info import AudioInfo  # pylint: disable=E0611, E0401
from libs.config_service import ConfigService  # pylint: disable=E0611, E0401
from libs.dsp import DSP  # pylint: disable=E0611, E0401
from libs.fps_limiter import FPSLimiter  # pylint: disable=E0611, E0401
from libs.notification_enum import NotificationEnum  # pylint: disable=E0611, E0401
from libs.notification_item import NotificationItem  # pylint: disable=E0611, E0401
from libs.queue_wrapper import QueueWrapper  # pylint: disable=E0611, E0401


class AudioProcessService:
    def start(self, config_lock, notification_queue_in, notification_queue_out, audio_queue, py_audio):
        self._config_lock = config_lock
        self._notification_queue_in = QueueWrapper(notification_queue_in)
        self._notification_queue_out = QueueWrapper(notification_queue_out)
        self._audio_queue = QueueWrapper(audio_queue)

        self.audio_buffer_queue = QueueWrapper(Queue(2))
        self._py_audio = py_audio
        self.stream = None

        self.init_audio_service(show_output=True)

        try:
            while True:
                self.audio_service_routine()
                self._fps_limiter.fps_limiter()
        except KeyboardInterrupt:
            sys.exit()

    def init_audio_service(self, show_output=False):
        try:
            # Initial config load.
            ConfigService.instance(self._config_lock).load_config()
            self._config = ConfigService.instance(self._config_lock).config

            # Init FPS Limiter.
            self._fps_limiter = FPSLimiter(120)
            self._skip_routine = False
            self._devices = AudioInfo.get_audio_devices(self._py_audio)

            self.log_output(show_output, "INFO", "Found the following audio sources:")

            # Select the audio device you want to use.
            selected_device_list_index = 0
            try:
                mic_id = self._config["general_settings"]["device_id"]
                # -1 means no mic available, we can return now to prevent further load
                if mic_id == -1:
                    return
                selected_device_list_index = int(mic_id)
            except Exception:
                logger.exception("Could not parse audio id.")

            # Check if the index is inside the list.
            self.selected_device = None
            # For each audio device, add to list of devices.
            for current_audio_device in self._devices:

                if current_audio_device.device_id == selected_device_list_index:
                    self.selected_device = current_audio_device

            logger.debug(f"Selected Device: {self.selected_device}")

            # Could not find a mic with the selected mic id, so I will use the first device I found.
            if self.selected_device is None:
                self.log_output(show_output, "ERROR",
                                "********************************************************")
                self.log_output(show_output, "ERROR",
                                "*                      Error                           *")
                self.log_output(show_output, "ERROR",
                                "********************************************************")
                self.log_output(show_output, "ERROR",
                                f"Could not find the mic with the id: {selected_device_list_index}")
                self.log_output(show_output, "ERROR",
                                "Using the first mic as fallback.")
                self.log_output(show_output, "ERROR",
                                "Please change the id of the mic inside the config.")
                try:
                    self.selected_device = self._devices[0]
                except IndexError:
                    self.selected_device = AudioInfo.get_default_audio_device(self._py_audio)

            self._device_rate = self._config["general_settings"]["default_sample_rate"]
            self._frames_per_buffer = self._config["general_settings"]["frames_per_buffer"]
            self.n_fft_bins = self._config["general_settings"]["n_fft_bins"]
            self.log_output(show_output, "INFO", f"Selected Device: {self.selected_device.to_string()}")

            # Init Timer
            self.start_time_1 = time()
            self.ten_seconds_counter_1 = time()
            self.start_time_2 = time()
            self.ten_seconds_counter_2 = time()

            self._dsp = DSP(self._config)

            self.audio = np.empty((self._frames_per_buffer), dtype="int16")

            # Reinit buffer queue
            self.audio_buffer_queue = QueueWrapper(Queue(2))

            # callback function to stream audio, another thread.
            def callback(in_data, frame_count, time_info, status):
                if self._skip_routine:
                    return (self.audio, pyaudio.paContinue)

                self.audio_buffer_queue.put_none_blocking(in_data)

                self.end_time_1 = time()

                if time() - self.ten_seconds_counter_1 > 10:
                    self.ten_seconds_counter_1 = time()
                    time_dif = self.end_time_1 - self.start_time_1
                    fps = 1 / time_dif
                    logger.info(f"Callback | FPS: {fps:.2f}")

                self.start_time_1 = time()

                return (self.audio, pyaudio.paContinue)

            self.log_output(show_output, "DEBUG", "Starting Open Audio Stream...")
            self.stream = self._py_audio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=self._device_rate,
                input=True,
                input_device_index=self.selected_device.device_id,
                frames_per_buffer=self._frames_per_buffer,
                stream_callback=callback
            )
        except Exception:
            logger.exception("Unexpected error in init_audio_service.")

    def log_output(self, show_output, log_level, message):
        if show_output:
            if log_level == "INFO":
                logger.info(message)
            elif log_level == "DEBUG":
                logger.debug(message)
            elif log_level == "ERROR":
                logger.error(message)
            else:
                logger.debug(message)
        else:
            logger.debug(message)

    def audio_service_routine(self):
        try:
            if not self._notification_queue_in.empty():
                current_notification_item = self._notification_queue_in.get_blocking()

                if current_notification_item.notification_enum is NotificationEnum.config_refresh:
                    if self.stream is not None:
                        self.stream.stop_stream()
                        self.stream.close()
                    self.init_audio_service()
                    self._notification_queue_out.put_blocking(NotificationItem(
                        NotificationEnum.config_refresh_finished, current_notification_item.device_id))
                elif current_notification_item.notification_enum is NotificationEnum.process_continue:
                    self._skip_routine = False
                elif current_notification_item.notification_enum is NotificationEnum.process_pause:
                    self._skip_routine = True

            if self._skip_routine:
                return

            in_data = None
            in_data = self.audio_buffer_queue.get_blocking_with_timeout()
            if in_data is None:
                logger.debug("Audio in timeout. Queue is Empty")
                return

            # Convert the raw string audio stream to an array.
            y = np.frombuffer(in_data, dtype=np.int16)
            # Use the type float32.
            y = y.astype(np.float32)

            # Process the audio stream.
            audio_datas = self._dsp.update(y)

            # Check if value is higher than min value.
            if audio_datas["vol"] < self._config["general_settings"]["min_volume_threshold"]:
                # Fill the array with zeros, to fade out the effect.
                audio_datas["mel"] = np.zeros(self.n_fft_bins)

            self._audio_queue.put_none_blocking(audio_datas)

            self.end_time_2 = time()

            if time() - self.ten_seconds_counter_2 > 10:
                self.ten_seconds_counter_2 = time()
                time_dif = self.end_time_2 - self.start_time_2
                fps = 1 / time_dif
                logger.info(f"Routine | FPS: {fps:.2f}")

            self.start_time_2 = time()

        except OSError:
            logger.exception("OSError while reading the Microphone Stream.")
        except Exception:
            logger.exception("Unexpected error in routine.")
