import numpy as np

from libs.effects.effect import Effect  # pylint: disable=E0611, E0401


class EffectPendulum(Effect):

    def __init__(self, device) -> None:

        # Call the constructor of the base class.
        super().__init__(device)

        # Pendulum Variables.
        self.current_direction = True
        self.current_position = 0
        self.current_color = [0, 0, 0]
        self.current_color_index = 0

    def run(self):
        # Get the config of the current effect.
        effect_config = self.get_effect_config("effect_pendulum")
        led_count = self._device.device_config["led_count"]

        if self.current_position in {0, led_count - 1}:
            if effect_config["change_color"]:
                gradient = self._config["gradients"][effect_config["gradient"]]
                count_colors_in_gradient = len(gradient)

                self.current_color_index += 1
                if self.current_color_index > count_colors_in_gradient - 1:
                    self.current_color_index = 0

                self.current_color = gradient[self.current_color_index]

            else:
                self.current_color = self._color_service.colour(effect_config["color"])

        # Build an empty array.
        output_array = np.zeros((3, self._device.device_config["led_count"]))

        # Calculate how many steps the array will roll.
        steps = self.get_roll_steps(effect_config["speed"])

        if self.current_direction:
            # start                                                       end
            # |-----------------------------------------------------------|
            #               ----> Direction

            # Fix the direction swap.
            if self.current_position == 0:
                self.current_position = effect_config["pendulum_length"]

            self.current_position += steps

            if self.current_position > led_count - 1:
                self.current_position = led_count - 1
                self.current_direction = False

            start_position = self.current_position
            end_position = start_position - effect_config["pendulum_length"]
            end_position = max(end_position, 0)

            output_array[0, end_position:start_position] = self.current_color[0]
            output_array[1, end_position:start_position] = self.current_color[1]
            output_array[2, end_position:start_position] = self.current_color[2]

        else:
            # end                                                       start
            # |-----------------------------------------------------------|
            #               <---- Direction

            # Fix the direction swap
            if self.current_position == led_count - 1:
                self.current_position = (led_count - 1) - effect_config["pendulum_length"]

            self.current_position -= steps

            if self.current_position < 0:
                self.current_position = 0
                self.current_direction = True

            start_position = self.current_position
            end_position = start_position + effect_config["pendulum_length"]
            end_position = min(end_position, led_count - 1)

            output_array[0, start_position:end_position] = self.current_color[0]
            output_array[1, start_position:end_position] = self.current_color[1]
            output_array[2, start_position:end_position] = self.current_color[2]

        # Add the output array to the queue.
        self.queue_output_array_blocking(output_array)
