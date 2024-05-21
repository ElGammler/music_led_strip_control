import numpy as np

from libs.effects.effect import Effect  # pylint: disable=E0611, E0401


class EffectBubble(Effect):
    def run(self):
        # Get the config of the current effect.
        effect_config = self.get_effect_config("effect_bubble")
        led_count = self._device.device_config["led_count"]
        led_mid = self._device.device_config["led_mid"]

        # Translate the true and false to a number, for the function use.
        current_reverse_translated = -1 if effect_config["reverse"] else 1

        full_bubble_ref = self._color_service.full_bubble

        # Build an array with the currently selected gradient.
        # Cut the slide to the led count length.
        output_array = np.array(
            [
                full_bubble_ref[effect_config["gradient"]][0][:led_count],
                full_bubble_ref[effect_config["gradient"]][1][:led_count],
                full_bubble_ref[effect_config["gradient"]][2][:led_count]
            ]
        )

        # Calculate how many steps the array will roll.
        steps = self.get_roll_steps(effect_config["speed"])

        # We got the current output array. Now we prepare the next step. We "roll" the array with the specified speed.
        full_bubble_ref[effect_config["gradient"]] = np.roll(
            full_bubble_ref[effect_config["gradient"]],
            steps * current_reverse_translated,
            axis=1
        )

        if effect_config["mirror"]:
            output_array = self.mirror_array(output_array, led_mid, led_count)

        # Add the output array to the queue.
        self.queue_output_array_blocking(output_array)
