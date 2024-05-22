import numpy as np

from libs.effects.effect import Effect


class EffectSyncFade(Effect):
    def run(self):
        # Get the config of the current effect.
        effect_config = self.get_effect_config("effect_sync_fade")

        # Prepare the required config inside local variables to enhance the looking of the long array functions.
        current_gradient = effect_config["gradient"]
        current_speed = effect_config["speed"]
        current_reverse = effect_config["reverse"]

        led_count = self._device.device_config["led_count"]

        current_color = self._device.color_service_global.get_global_fade_color(current_speed, current_gradient, current_reverse)

        # Get the current color we will use for the whole led strip.
        current_color_r = current_color[0]
        current_color_g = current_color[1]
        current_color_b = current_color[2]

        # Fill the whole strip with the color.
        output_array = np.array(
            [
                [current_color_r for i in range(led_count)],
                [current_color_g for i in range(led_count)],
                [current_color_b for i in range(led_count)]
            ]
        )

        # Add the output array to the queue.
        self.queue_output_array_blocking(output_array)
