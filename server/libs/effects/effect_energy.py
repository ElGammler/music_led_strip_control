import numpy as np
from scipy.ndimage import gaussian_filter1d

from libs.effects.effect import Effect  # pylint: disable=E0611, E0401


class EffectEnergy(Effect):
    def run(self):
        effect_config = self.get_effect_config("effect_energy")
        led_count = self._device.device_config["led_count"]
        led_mid = self._device.device_config["led_mid"]

        audio_data = self.get_audio_data()
        y = self.get_mel(audio_data)

        if y is None:
            return

        y = np.copy(y)
        self._dsp.gain.update(y)
        y /= self._dsp.gain.value
        scale = effect_config["scale"]
        # Scale by the width of the LED strip.
        y *= float((led_count * scale) - 1)
        y = np.copy(self._math_service.interpolate(y, led_count // 2))
        # Map color channels according to energy in the different freq bands.
        self.prev_spectrum = np.copy(y)
        spectrum = np.copy(self.prev_spectrum)
        spectrum = np.array([j for i in zip(spectrum, spectrum) for j in i])
        # Color channel mappings.
        r = int(np.mean(spectrum[:len(spectrum) // 3]**scale) * effect_config["r_multiplier"])
        g = int(np.mean(spectrum[len(spectrum) // 3: 2 * len(spectrum) // 3]**scale) * effect_config["g_multiplier"])
        b = int(np.mean(spectrum[2 * len(spectrum) // 3:]**scale) * effect_config["b_multiplier"])
        # Assign color to different frequency regions.
        self.output[0, :r] = 255
        self.output[0, r:] = 0
        self.output[1, :g] = 255
        self.output[1, g:] = 0
        self.output[2, :b] = 255
        self.output[2, b:] = 0
        # Apply blur to smooth the edges.
        blur_amount = effect_config["blur"]
        if blur_amount > 0:
            self.output[0, :] = gaussian_filter1d(self.output[0, :], sigma=blur_amount)
            self.output[1, :] = gaussian_filter1d(self.output[1, :], sigma=blur_amount)
            self.output[2, :] = gaussian_filter1d(self.output[2, :], sigma=blur_amount)

        output_array = self.mirror_array(self.output, led_mid, led_count) if effect_config["mirror"] else self.output

        self.queue_output_array_noneblocking(output_array)
