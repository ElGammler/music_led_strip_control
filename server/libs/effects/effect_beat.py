import random

import numpy as np

from libs.effects.effect import Effect


class EffectBeat(Effect):

    def __init__(self, device) -> None:
        # Call the constructor of the base class.
        super().__init__(device)
        # Setup for "EffectBeat" (don't change this).
        self.gradient_position = 0

    def run(self):
        """Effect that flashes to the beat."""
        effect_config = self.get_effect_config("effect_beat")
        led_count = self._device.device_config["led_count"]
        current_gradient = effect_config["gradient"]
        use_random_color = effect_config["random_color"]
        colorful_mode = effect_config["colorful_mode"]

        audio_data = self.get_audio_data()
        y = self.get_mel(audio_data)

        if y is None:
            return

        self.update_freq_channels(y)
        self.detect_freqs()

        output = np.zeros((3, led_count))

        if self.current_freq_detects["beat"]:
            if colorful_mode:
                full_gradient_ref = self._color_service.full_gradients

                if use_random_color:
                    self.gradient_position = random.randrange(0, len(full_gradient_ref[current_gradient][0]), 1)

                else:
                    self.gradient_position += 1
                    if self.gradient_position >= len(full_gradient_ref[current_gradient][0]):
                        self.gradient_position = 0

                output[0][:] = full_gradient_ref[current_gradient][0][self.gradient_position]
                output[1][:] = full_gradient_ref[current_gradient][1][self.gradient_position]
                output[2][:] = full_gradient_ref[current_gradient][2][self.gradient_position]

            else:
                output[0][:] = self._color_service.colour(effect_config["color"])[0]
                output[1][:] = self._color_service.colour(effect_config["color"])[1]
                output[2][:] = self._color_service.colour(effect_config["color"])[2]
        else:
            output = np.copy(self.prev_output)
            output = np.multiply(self.prev_output, effect_config["decay"])

        self.queue_output_array_noneblocking(output)

        self.prev_output = output
