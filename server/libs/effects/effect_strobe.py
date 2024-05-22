from time import time

import numpy as np

from libs.effects.effect import Effect


class EffectStrobe(Effect):

    def __init__(self, device) -> None:

        # Call the constructor of the base class.
        super().__init__(device)

        # Used to calculate time between strobe states.
        self.now = time() * 1000
        self.last_time = self.now

        # False - strobe OFF, True - strobe ON.
        self.current_state = False

    def run(self):
        # Get the config of the current effect.
        effect_config = self.get_effect_config("effect_strobe")
        self._led_strip = self._device.device_config["led_strip"]

        speed = effect_config["speed"]

        self.now = time() * 1000

        if (self.now - self.last_time) > (1000 / speed):
            self.last_time = time() * 1000
            self.current_state = not self.current_state

        # Build an empty array.
        if "sk6812" in self._led_strip:
            output_array = np.zeros((4, self._device.device_config["led_count"]))
        else:
            output_array = np.zeros((3, self._device.device_config["led_count"]))

        if self.current_state:
            color = effect_config["custom_color"] if effect_config["use_custom_color"] else self._config_colours[effect_config["color"]]
        else:
            color = self._config_colours["black"]

        # Fill the array with the selected color.
        for i in range(3):
            output_array[i][:] = color[i]

        if "sk6812" in self._led_strip:
            output_array[3][:] = effect_config["white"]

        # Add the output array to the queue.
        self.queue_output_array_blocking(output_array)
