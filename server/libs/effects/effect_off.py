import numpy as np

from libs.effects.effect import Effect


class EffectOff(Effect):
    def run(self):
        # Build an empty array.
        output_array = np.zeros((3, self._device.device_config["led_count"]))

        self.queue_output_array_blocking(output_array)
