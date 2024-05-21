import numpy as np

from libs.effects.effect import Effect  # pylint: disable=E0611, E0401


class EffectRods(Effect):

    def __init__(self, device) -> None:

        # Call the constructor of the base class.
        super().__init__(device)

        # Rods Variables.
        self.count_since_last_rod = 0
        self.current_color = [0, 0, 0]
        self.current_color_index = 0

    def run(self):
        # Get the config of the current effect.
        effect_config = self.get_effect_config("effect_rods")
        led_count = self._device.device_config["led_count"]
        led_mid = self._device.device_config["led_mid"]

        self.count_since_last_rod += 1

        # Calculate how many steps the array will roll.
        steps = self.get_roll_steps(effect_config["speed"])

        # Not reverse
        # start                         end
        # |-------------------------------|
        # Move array ---> this direction for "steps" fields

        # Reverse
        # start                         end
        # |-------------------------------|
        # Move array <--- this direction for "steps" fields

        # Build an empty array.
        local_output_array = np.zeros((3, self._device.device_config["led_count"]))

        if not effect_config["reverse"]:
            self.output = np.roll(self.output, steps, axis=1)
            self.output[:, :steps] = np.zeros((3, steps))
        else:
            self.output = np.roll(self.output, steps * -1, axis=1)
            self.output[:, led_count - steps:] = np.zeros((3, steps))

        if (self.count_since_last_rod - effect_config["rods_length"]) > effect_config["rods_distance"]:
            self.count_since_last_rod = 0

            # FInd the next color.
            if effect_config["change_color"]:
                gradient = self._config["gradients"][effect_config["gradient"]]
                count_colors_in_gradient = len(gradient)

                self.current_color_index += 1
                if self.current_color_index > count_colors_in_gradient - 1:
                    self.current_color_index = 0

                self.current_color = gradient[self.current_color_index]

            else:
                self.current_color = self._color_service.colour(effect_config["color"])

        if self.count_since_last_rod <= effect_config["rods_length"]:
            if not effect_config["reverse"]:
                self.output[0, :steps] = self.current_color[0]
                self.output[1, :steps] = self.current_color[1]
                self.output[2, :steps] = self.current_color[2]
            else:
                self.output[0, led_count - steps:] = self.current_color[0]
                self.output[1, led_count - steps:] = self.current_color[1]
                self.output[2, led_count - steps:] = self.current_color[2]

        local_output_array = self.output

        if effect_config["mirror"]:
            local_output_array = self.mirror_array(local_output_array, led_mid, led_count)

        # Add the output array to the queue.
        self.queue_output_array_blocking(local_output_array)
