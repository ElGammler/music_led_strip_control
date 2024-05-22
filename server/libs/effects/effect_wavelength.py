import numpy as np
from scipy.ndimage import gaussian_filter1d

from libs.effects.effect import Effect


class EffectWavelength(Effect):
    def run(self):
        effect_config = self.get_effect_config("effect_wavelength")
        led_count = self._device.device_config["led_count"]
        led_mid = self._device.device_config["led_mid"]

        audio_data = self.get_audio_data()
        y = self.get_mel(audio_data)

        if y is None:
            return

        # Interpolate y to get an array, which is half as long as the LED strip.
        y = np.copy(self._math_service.interpolate(y, led_count // 2))
        self._dsp.common_mode.update(y)

        # Color channel mappings.
        r = self._dsp.r_filt.update(y - self._dsp.common_mode.value)

        # Expand the array twice the size and mirror the values.
        # [0,1,2,3]
        # --> [0,1,2,3,3,2,1,0]
        r = np.array([j for i in zip(r, r) for j in i])

        # If the r array is smaller than the led_count, the r array will be filled with the last value.
        r_len_before_resize = len(r)
        missing_values = led_count - r_len_before_resize
        r = np.pad(r, (0, missing_values), "edge")

        start_gradient_index = (led_count if effect_config["reverse_grad"] else 0)
        end_gradient_index = (None if effect_config["reverse_grad"] else led_count)

        self.output = np.array(
            [
                self._color_service.full_gradients[effect_config["color_mode"]][0][start_gradient_index:end_gradient_index:] * r,
                self._color_service.full_gradients[effect_config["color_mode"]][1][start_gradient_index:end_gradient_index:] * r,
                self._color_service.full_gradients[effect_config["color_mode"]][2][start_gradient_index:end_gradient_index:] * r
            ]
        )

        # Calculate how many steps the array will roll.
        steps = self.get_roll_steps(effect_config["roll_speed"])

        self._color_service.full_gradients[effect_config["color_mode"]] = np.roll(
            self._color_service.full_gradients[effect_config["color_mode"]],
            steps * (-1 if effect_config["reverse_roll"] else 1),
            axis=1
        )
        blur_amount = effect_config["blur"]
        if blur_amount > 0:
            self.output[0] = gaussian_filter1d(self.output[0], sigma=blur_amount)
            self.output[1] = gaussian_filter1d(self.output[1], sigma=blur_amount)
            self.output[2] = gaussian_filter1d(self.output[2], sigma=blur_amount)

        if effect_config["flip_lr"]:
            self.output = np.fliplr(self.output)

        if effect_config["mirror"]:
            self.output = self.mirror_array(self.output, led_mid, led_count)

        self.queue_output_array_noneblocking(self.output)
