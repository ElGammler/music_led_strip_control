from collections import deque
from time import time

import numpy as np

from libs.color_service import ColorService  # pylint: disable=E0611, E0401
from libs.dsp import DSP  # pylint: disable=E0611, E0401
from libs.math_service import MathService  # pylint: disable=E0611, E0401


class Effect:

    def __init__(self, device) -> None:
        self._device = device

        # Initial config load.
        self._config = self._device.config
        self._config_colours = self._config["colors"]
        self._config_gradients = self._config["gradients"]

        self._device_config = self._device.device_config
        self._output_queue = self._device.output_queue
        self._audio_queue = self._device.audio_queue

        # Initialize color service and build gradients.
        self._color_service = ColorService(self._config, self._device_config)
        self._color_service.build_gradients()
        self._color_service.build_fadegradients()
        self._color_service.build_slidearrays()
        self._color_service.build_slidearrays()
        self._color_service.build_bubblearrays()

        # Init math service.
        self._math_service = MathService()

        # Init dsp.
        self._dsp = DSP(self._config, self._device_config)

        # Init some variables for the effects.
        self.led_count = self._device_config["led_count"]
        self.n_fft_bins = self._config["general_settings"]["n_fft_bins"]

        self.prev_spectrum = np.array([self.led_count // 2])
        self.freq_channel_history = 40
        self.beat_count = 0
        self.freq_channels = [deque(maxlen=self.freq_channel_history)
                              for i in range(self.n_fft_bins)]

        self.output = np.array(
            [[0 for i in range(self.led_count)] for i in range(3)])
        self.prev_output = np.array(
            [[0 for i in range(self.led_count)] for i in range(3)])

        self.speed_counter = 0

        self.current_freq_detects = {
            "beat": False,
            "low": False,
            "mid": False,
            "high": False
        }
        self.prev_freq_detects = {
            "beat": 0,
            "low": 0,
            "mid": 0,
            "high": 0
        }
        self.detection_ranges = {
            "beat": (0, int(self._config["general_settings"]["n_fft_bins"] * 0.13)),
            "low": (int(self._config["general_settings"]["n_fft_bins"] * 0.13),
                    int(self._config["general_settings"]["n_fft_bins"] * 0.4)),
            "mid": (int(self._config["general_settings"]["n_fft_bins"] * 0.4),
                    int(self._config["general_settings"]["n_fft_bins"] * 0.7)),
            "high": (int(self._config["general_settings"]["n_fft_bins"] * 0.8),
                     int(self._config["general_settings"]["n_fft_bins"]))
        }
        self.min_detect_amplitude = {
            "beat": 0.7,
            "low": 0.5,
            "mid": 0.3,
            "high": 0.3
        }
        self.min_percent_diff = {
            "beat": 70,
            "low": 100,
            "mid": 50,
            "high": 30
        }

        # Setup for "Power" (don't change these).
        self.power_indexes = []
        self.power_brightness = 0

        # Setup for "Wave" (don't change this).
        self.wave_wipe_count = 0

    def run(self):
        raise NotImplementedError

    def update_freq_channels(self, y):
        for i, _ in enumerate(y):
            self.freq_channels[i].appendleft(y[i])

    def detect_freqs(self):
        """Update current_freq_detects.

        Any visualisation algorithm can check if there is currently a beat,
        low, mid, or high by querying the self.current_freq_detects dict.
        """
        n_fft_bins = self._config["general_settings"]["n_fft_bins"]
        channel_avgs = []
        differences = []

        for i in range(n_fft_bins):
            channel_avgs.append(
                sum(self.freq_channels[i]) / len(self.freq_channels[i]))
            if channel_avgs[i] != 0:
                differences.append(
                    ((self.freq_channels[i][0] - channel_avgs[i]) * 100) // channel_avgs[i])
            else:
                differences.append(0)
        for i in ["beat", "low", "mid", "high"]:
            if (any(differences[j] >= self.min_percent_diff[i]
                    and self.freq_channels[j][0] >= self.min_detect_amplitude[i]
                    for j in range(*self.detection_ranges[i]))
                and (time() - self.prev_freq_detects[i] > 0.2)
                    and len(self.freq_channels[0]) == self.freq_channel_history):
                self.prev_freq_detects[i] = time()
                self.current_freq_detects[i] = True
            else:
                self.current_freq_detects[i] = False

    def get_roll_steps(self, current_speed):
        """Calculate the steps for the rollspeed.

        Up to 1 you can adjust the speed very fine. After this, you need to add decades to increase the speed.
        """
        max_counter = 1
        steps = 0

        self.speed_counter += current_speed

        if self.speed_counter > max_counter:
            self.speed_counter = 0

            steps = int(1 / (max_counter / current_speed)) if max_counter / current_speed < 1 else 1

        else:
            steps = 0

        return steps

    def get_audio_data(self):
        audio_data = None
        if not self._audio_queue.empty():
            audio_data = self._audio_queue.get_blocking()

        return audio_data

    @staticmethod
    def get_mel(audio_data):

        # Audio Data is empty.
        if (audio_data is None):
            return None

        audio_mel = audio_data["mel"]

        # mel is empty.
        if (audio_mel is None):
            return None

        return audio_mel

    @staticmethod
    def get_vol(audio_data):

        # Audio Data is empty.
        if (audio_data is None):
            return None

        audio_vol = audio_data["vol"]

        # vol is empty.
        if (audio_vol is None):
            return None

        return audio_vol

    def queue_output_array_blocking(self, output_array):
        self._output_queue.put_blocking(output_array)

    def queue_output_array_noneblocking(self, output_array):
        self._output_queue.put_none_blocking(output_array)

    def get_effect_config(self, effect_id):
        return self._device.device_config["effects"][effect_id]

    @staticmethod
    def mirror_array(array, led_mid, led_count):
        # Calculate the real mid
        # |                   |real_mid             |
        # |---------------------------|-------------|
        # |                         led_mid (set in config)

        real_mid = led_count / 2

        # Add some tolerance for the real mid.
        if (real_mid >= led_mid - 2) and (real_mid <= led_mid + 2):
            # Use the option with shrinking the array.
            return np.concatenate((array[:, ::-2], array[:, ::2]), axis=1)

        # Mirror the whole array. After this the array has the double size than led_count.
        big_mirrored_array = np.concatenate(
            (array[:, ::-1], array[:, ::1]), axis=1)
        start_of_array = led_count - led_mid
        end_of_array = start_of_array + led_count

        return big_mirrored_array[:, start_of_array:end_of_array]
