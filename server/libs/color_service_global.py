from time import time

import numpy as np
from loguru import logger


class ColorServiceGlobal:
    def __init__(self, config) -> None:
        self._config = config
        device_config = {}
        if len(self._config["device_configs"].keys()) > 0:
            device_key = next(iter(self._config["device_configs"].keys()))
            device_config = self._config["device_configs"][device_key]
        else:
            device_config = self._config["default_device"]

        self._device_config = device_config
        self.full_gradients = {}
        self.full_fadegradients = {}
        self.full_slide = {}
        self.full_bubble = {}

        self.build_gradients()
        self.current_fade_color = {}
        self.current_fade_color[0] = 0
        self.current_fade_color[1] = 0
        self.current_fade_color[2] = 0
        self.last_fade_change_time = int(round(time() * 1000))

    def build_gradients(self):
        led_count = 1000

        self.full_gradients = {}

        for key in self._config["gradients"]:
            not_mirrored_gradient = self._easing_gradient_generator(
                self._config["gradients"][key],  # All colors of the current gradient.
                led_count
            )

            # Mirror the gradient to get seamless transition from start to the end.
            # [1,2,3,4]
            # -> [1,2,3,4,4,3,2,1]
            self.full_gradients[key] = np.concatenate(
                (not_mirrored_gradient[:, ::-1], not_mirrored_gradient),
                axis=1
            )

    @staticmethod
    def _easing_gradient_generator(colors: list, length: int):
        """Return np.array of given length that eases between specified colors.

        Parameters
        ----------
        colors: list, colors must be in self.config.colour_manager["colors"]
            eg. ["red", "orange", "blue", "purple"]
        length: int, length of array to return. should be from self.config.settings
            eg. self.config.settings["devices"]["my strip"]["configuration"]["N_PIXELS"]

        """
        def _easing_func(x, length, slope=2.5):
            # Returns a nice eased curve with defined length and curve.
            xa = (x / length)**slope
            return xa / (xa + (1 - (x / length))**slope)
        colors.reverse()  # Needs to be reversed, makes it easier to deal with.
        n_transitions = len(colors) - 1
        ease_length = length // n_transitions
        pad = length - (n_transitions * ease_length)
        output = np.zeros((3, length))
        ease = np.array([_easing_func(i, ease_length, slope=2.5) for i in range(ease_length)])
        # For r,g,b.
        for i in range(3):
            # For each transition.
            for j in range(n_transitions):
                # Starting ease value.
                start_value = colors[j][i]
                # Ending ease value.
                end_value = colors[j + 1][i]
                # Difference between start and end.
                diff = end_value - start_value
                # Make array of all starting values.
                base = np.empty(ease_length)
                base.fill(start_value)
                # Make array of the difference between start and end.
                diffs = np.empty(ease_length)
                diffs.fill(diff)
                # Run diffs through easing function to make smooth curve.
                eased_diffs = diffs * ease
                # Add transition to base values to produce curve from start to end value.
                base += eased_diffs
                # Append this to the output array.
                output[i, j * ease_length:(j + 1) * ease_length] = base
        # Cast to int.
        output = np.asarray(output, dtype=int)
        # Pad out the ends (bit messy but it works and looks good).
        if pad:
            for i in range(3):
                output[i, -pad:] = output[i, -pad - 1]
        return output

    def colour(self, colour):
        """Return the values of a given color.

        Use this function to get color values.
        """
        if colour in self._config["colors"]:
            return self._config["colors"][colour]
        logger.error(f"Color '{colour}' has not been defined.")
        return (0, 0, 0)

    def get_global_fade_color(self, fade_speed, fade_gradient, fade_reverse):
        current_time = int(round(time() * 1000))
        time_diff = current_time - self.last_fade_change_time

        rolling_steps = int((fade_speed * time_diff) / 500)

        if rolling_steps >= 1:
            current_reverse_translated = -1 if fade_reverse else 1

            self.full_gradients[fade_gradient] = np.roll(
                self.full_gradients[fade_gradient],
                rolling_steps * current_reverse_translated,
                axis=1
            )

            self.last_fade_change_time = int(round(time() * 1000))

        self.current_fade_color[0] = self.full_gradients[fade_gradient][0][0]
        self.current_fade_color[1] = self.full_gradients[fade_gradient][1][0]
        self.current_fade_color[2] = self.full_gradients[fade_gradient][2][0]

        return self.current_fade_color
