import numpy as np

from libs.effects.effect import Effect


class EffectFade(Effect):
    def run(self):
        # Get the config of the current effect.
        effect_config = self.get_effect_config("effect_fade")

        # Prepare the required config inside local variables to enhance the looking of the long array functions.
        current_gradient = effect_config["gradient"]
        current_speed = effect_config["speed"]
        current_reverse = effect_config["reverse"]

        led_count = self._device.device_config["led_count"]

        # Translate the true and false to a number, for the function use.
        current_reverse_translated = -1 if current_reverse else 1

        full_gradient_ref = self._color_service.full_fadegradients

        # Get the current color we will use for the whole led strip.
        current_color_r = full_gradient_ref[current_gradient][0][0]
        current_color_g = full_gradient_ref[current_gradient][1][0]
        current_color_b = full_gradient_ref[current_gradient][2][0]

        # Fill the whole strip with the color.
        output_array = np.array([
            [current_color_r for i in range(led_count)],
            [current_color_g for i in range(led_count)],
            [current_color_b for i in range(led_count)]
        ])

        # Calculate how many steps the array will roll.
        steps = self.get_roll_steps(current_speed)

        # We got the current output array. Now we prepare the next step. We "roll" the array with the specified speed.
        full_gradient_ref[current_gradient] = np.roll(
            full_gradient_ref[current_gradient],
            steps * current_reverse_translated,
            axis=1
        )

        # Add the output array to the queue.
        self.queue_output_array_blocking(output_array)
