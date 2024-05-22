import random

import numpy as np

from libs.effects.effect import Effect


class EffectPower(Effect):
    def run(self):
        effect_config = self.get_effect_config("effect_power")
        led_count = self._device.device_config["led_count"]
        n_fft_bins = self._config["general_settings"]["n_fft_bins"]
        led_mid = self._device.device_config["led_mid"]

        audio_data = self.get_audio_data()
        y = self.get_mel(audio_data)

        if y is None:
            return

        self.update_freq_channels(y)
        self.detect_freqs()

        # Bit of fiddling with the y values.
        y = np.copy(self._math_service.interpolate(y, led_count // 2))
        self._dsp.common_mode.update(y)
        self.prev_spectrum = np.copy(y)
        # Color channel mappings.
        r = self._dsp.r_filt.update(y - self._dsp.common_mode.value)
        r = np.array([j for i in zip(r, r) for j in i])
        # If the r array is smaller than the led_count, the r array will be filled with the last value.
        r_len_before_resize = len(r)
        missing_values = led_count - r_len_before_resize
        r = np.pad(r, (0, missing_values), "edge")

        output = np.array([self._color_service.full_gradients[effect_config["color_mode"]][0, :led_count] * r,
                           self._color_service.full_gradients[effect_config["color_mode"]][1, :led_count] * r,
                           self._color_service.full_gradients[effect_config["color_mode"]][2, :led_count] * r])
        # if there's a high (eg. clap):
        if self.current_freq_detects["high"]:
            self.power_brightness = 1.0
            # Generate random indices.
            self.power_indexes = random.sample(range(led_count), effect_config["s_count"])
        # Assign color to the random indices.
        for index in self.power_indexes:
            output[0, index] = int(self._color_service.colour(effect_config["s_color"])[0] * self.power_brightness)
            output[1, index] = int(self._color_service.colour(effect_config["s_color"])[1] * self.power_brightness)
            output[2, index] = int(self._color_service.colour(effect_config["s_color"])[2] * self.power_brightness)
        # Remove some of the indices for next time.
        self.power_indexes = [i for i in self.power_indexes if i not in random.sample(self.power_indexes, len(self.power_indexes) // 4)]
        if len(self.power_indexes) <= 4:
            self.power_indexes = []
        # Fade the color of the sparks out a bit for next time.
        if self.power_brightness > 0:
            self.power_brightness -= 0.05
        # Calculate length of bass bar based on max bass frequency volume and length of strip.
        strip_len = int((led_count // 3) * max(y[:int(n_fft_bins * 0.2)]))
        # Add the bass bars into the output. Color proportional to length.
        output[0][:strip_len] = self._color_service.full_gradients[effect_config["color_mode"]][0][strip_len]
        output[1][:strip_len] = self._color_service.full_gradients[effect_config["color_mode"]][1][strip_len]
        output[2][:strip_len] = self._color_service.full_gradients[effect_config["color_mode"]][2][strip_len]
        if effect_config["flip_lr"]:
            output = np.fliplr(output)

        if effect_config["mirror"]:
            output = self.mirror_array(output, led_mid, led_count)

        self.queue_output_array_noneblocking(output)
