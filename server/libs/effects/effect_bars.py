import numpy as np

from libs.effects.effect import Effect


class EffectBars(Effect):
    def run(self):
        effect_config = self.get_effect_config("effect_bars")
        led_count = self._device.device_config["led_count"]
        led_mid = self._device.device_config["led_mid"]

        audio_data = self.get_audio_data()
        y = self.get_mel(audio_data)

        if y is None:
            return

        # Bit of fiddling with the y values.
        y = np.copy(self._math_service.interpolate(y, led_count // 2))
        self._dsp.common_mode.update(y)
        self.prev_spectrum = np.copy(y)
        # Color channel mappings.
        r = self._dsp.r_filt.update(y - self._dsp.common_mode.value)
        r = np.array([j for i in zip(r, r) for j in i])
        # Split y into [resolution] chunks and calculate the average of each.
        max_values = np.array([max(i) for i in np.array_split(r, effect_config["resolution"])])
        max_values = np.clip(max_values, 0, 1)

        color_sets = [
            # [r,g,b] values from a multicolor gradient array at [resolution] equally spaced intervals.
            [
                self._color_service.full_gradients[effect_config["color_mode"]][j][i * (led_count // effect_config["resolution"])]
                for j in range(3)
            ]
            for i in range(effect_config["resolution"])
        ]

        output = np.zeros((3, led_count))
        chunks = np.array_split(output[0], effect_config["resolution"])
        n = 0
        # Assign blocks with heights corresponding to max_values and colors from color_sets.
        for i, _ in enumerate(chunks):
            m = len(chunks[i])
            for j in range(3):
                output[j][n:n + m] = color_sets[i][j] * max_values[i]
            n += m

        # Calculate how many steps the array will roll.
        steps = self.get_roll_steps(effect_config["roll_speed"])

        self._color_service.full_gradients[effect_config["color_mode"]] = np.roll(
            self._color_service.full_gradients[effect_config["color_mode"]],
            steps * (-1 if effect_config["reverse_roll"] else 1),
            axis=1
        )
        if effect_config["flip_lr"]:
            output = np.fliplr(output)

        if effect_config["mirror"]:
            output = self.mirror_array(output, led_mid, led_count)

        self.queue_output_array_noneblocking(output)
