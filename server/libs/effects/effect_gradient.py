import numpy as np

from libs.effects.effect import Effect  # pylint: disable=E0611, E0401


class EffectGradient(Effect):
    def run(self):
        # Get the config of the current effect.
        effect_config = self.get_effect_config("effect_gradient")

        # Prepare the required config inside local variables to enhance the looking of the long array functions.
        current_gradient = effect_config["gradient"]
        current_speed = effect_config["speed"]
        current_reverse = effect_config["reverse"]

        led_count = self._device.device_config["led_count"]
        led_mid = self._device.device_config["led_mid"]

        # Translate the true and false to a number, for the function use.
        current_reverse_translated = -1 if current_reverse else 1

        full_gradient_ref = self._color_service.full_gradients

        # Build an array with the current selected gradient.
        # Cut the full gradient to the led count length.
        output_array = np.array(
            [
                full_gradient_ref[current_gradient][0][:led_count],
                full_gradient_ref[current_gradient][1][:led_count],
                full_gradient_ref[current_gradient][2][:led_count]
            ]
        )

        # Calculate how many steps the array will roll
        steps = self.get_roll_steps(current_speed)

        # We got the current output array. Now we prepare the next step. We "roll" the array with the specified speed.
        full_gradient_ref[current_gradient] = np.roll(
            full_gradient_ref[current_gradient],
            steps * current_reverse_translated,
            axis=1
        )

        if effect_config["mirror"]:
            output_array = self.mirror_array(output_array, led_mid, led_count)

        # Add the output array to the queue.
        self.queue_output_array_blocking(output_array)
