import random

import numpy as np

from libs.effects.effect import Effect


class EffectDirectionChanger(Effect):
    def __init__(self, device) -> None:
        # Call the constructor of the base class.
        super().__init__(device)
        self.gradient_position = 0

        # Example
        # led_count = 7
        # led_mid = 3

        #                 <---  |  --->
        # --------------------------------------------------------
        # |  0   |   1   |   2   |   3   |   4   |   5   |   6   |
        # --------------------------------------------------------
        #
        # |        left          |                right          |
        #
        # Console Example
        # >>> s = [0,1,2,3,4,5,6]
        # >>> s
        # [0, 1, 2, 3, 4, 5, 6]
        #
        # >>> s[0:3]
        # [0, 1, 2]
        #
        # >>> s[3:7]
        # [3, 4, 5, 6]
        #

        # Variable Example
        # self.output_left_length = 3
        # self.output_left_min_index = 0
        # self.output_left_max_index = 3
        #
        # self.output_right_length = 4
        # self.output_right_min_index = 3
        # self.output_right_max_index = 7
        #
        #

        self.output_left_length = self._device.device_config["led_mid"]

        # Set effect middle to center if value is outside the led_count range.
        if not 0 < self.output_left_length < self._device.device_config["led_count"]:
            self.output_left_length = self._device.device_config["led_count"] // 2

        self.output_left_min_index = 0
        self.output_left_max_index = self.output_left_length

        self.output_right_length = self._device.device_config["led_count"] - self.output_left_length
        self.output_right_min_index = self.output_left_max_index
        self.output_right_max_index = self.output_right_min_index + self.output_right_length

        #
        # >>> import numpy as np
        # >>> self.output_left = np.zeros((3,3))
        #
        # >>> output_left = np.zeros((3,3))
        # >>> output_left[0]
        # array([0., 0., 0.])
        # >>> output_right = np.zeros((3,4))
        # >>> output_right[0]
        # array([0., 0., 0., 0.])

        self.output_left = np.zeros((3, self.output_left_length))
        self.output_right = np.zeros((3, self.output_right_length))

        # -1 = left
        # 1 = right
        self.current_direction = 1

        self.bars_in_the_same_direction = 0

        self.current_bar_length_left = 0
        self.current_bar_length_right = 0

    def run(self):
        effect_config = self.get_effect_config("effect_direction_changer")
        led_count = self._device.device_config["led_count"]

        current_gradient = effect_config["gradient"]
        use_random_color = effect_config["random_color"]
        colorful_mode = effect_config["colorful_mode"]
        bars_in_same_direction = effect_config["bars_in_same_direction"]
        bar_length = effect_config["bar_length"]
        bar_speed = effect_config["bar_speed"]

        # Calculate how many steps the array will roll.
        steps = self.get_roll_steps(bar_speed)
        if steps <= 0:
            return

        audio_data = self.get_audio_data()
        y = self.get_mel(audio_data)

        if y is None:
            return

        self.update_freq_channels(y)
        self.detect_freqs()

        output = np.zeros((3, led_count))

        ###############
        # Prepare left
        ###############

        # Shift previous output to prepare next bars and finish the running ones.
        current_output_left = np.copy(self.output_left)
        last_left_color = [0, 0, 0]
        last_left_color[0] = current_output_left[0][-1]
        last_left_color[1] = current_output_left[1][-1]
        last_left_color[2] = current_output_left[2][-1]

        # We got the current output array. Now we prepare the next step. We "roll" the array with the specified speed.
        current_output_left = np.roll(
            current_output_left,
            -1 * steps,
            axis=1
        )

        # Fill rolled pixels with black.
        left_index = (self.output_left_length - steps)

        current_output_left[0][left_index:] = 0
        current_output_left[1][left_index:] = 0
        current_output_left[2][left_index:] = 0

        if self.current_bar_length_left < bar_length and self.current_bar_length_left > 0:
            missing_bar_leds = min(steps, bar_length - self.current_bar_length_left)

            left_index = (self.output_left_length - steps)
            right_index = (self.output_left_length - steps) + missing_bar_leds

            current_output_left[0][left_index:right_index] = last_left_color[0]
            current_output_left[1][left_index:right_index] = last_left_color[1]
            current_output_left[2][left_index:right_index] = last_left_color[2]

            self.current_bar_length_left += missing_bar_leds
            if self.current_bar_length_left >= bar_length:
                self.current_bar_length_left = 0

        ###############
        # Prepare right
        ###############

        # Shift previous output to prepare next bars and finish the running ones.
        current_output_right = np.copy(self.output_right)
        last_right_color = [0, 0, 0]
        last_right_color[0] = current_output_right[0][0]
        last_right_color[1] = current_output_right[1][0]
        last_right_color[2] = current_output_right[2][0]

        # We got the current output array. Now we prepare the next step. We "roll" the array with the specified speed.
        current_output_right = np.roll(
            current_output_right,
            1 * steps,
            axis=1
        )

        # Fill rolled pixels with black
        right_index = steps

        current_output_right[0][:right_index] = 0
        current_output_right[1][:right_index] = 0
        current_output_right[2][:right_index] = 0

        if self.current_bar_length_right < bar_length and self.current_bar_length_right > 0:
            missing_bar_leds = min(steps, bar_length - self.current_bar_length_right)

            left_index = (steps - missing_bar_leds) - 1
            left_index = max(left_index, 0)
            right_index = steps

            current_output_right[0][left_index:right_index] = last_right_color[0]
            current_output_right[1][left_index:right_index] = last_right_color[1]
            current_output_right[2][left_index:right_index] = last_right_color[2]

            self.current_bar_length_right += missing_bar_leds
            if self.current_bar_length_right >= bar_length:
                self.current_bar_length_right = 0

        # Add new bar.
        if self.current_freq_detects["beat"]:
            current_color_for_bar = [0, 0, 0]

            if colorful_mode:
                full_gradient_ref = self._color_service.full_gradients

                if use_random_color:
                    self.gradient_position = random.randrange(0, len(full_gradient_ref[current_gradient][0]), 1)

                else:
                    self.gradient_position += 1
                    if self.gradient_position >= len(full_gradient_ref[current_gradient][0]):
                        self.gradient_position = 0

                current_color_for_bar[0] = full_gradient_ref[current_gradient][0][self.gradient_position]
                current_color_for_bar[1] = full_gradient_ref[current_gradient][1][self.gradient_position]
                current_color_for_bar[2] = full_gradient_ref[current_gradient][2][self.gradient_position]

            else:
                current_color_for_bar[0] = self._color_service.colour(effect_config["color"])[0]
                current_color_for_bar[1] = self._color_service.colour(effect_config["color"])[1]
                current_color_for_bar[2] = self._color_service.colour(effect_config["color"])[2]

            # Check how many bars are already in the same direction. Change the direction and increase/reset the counter.
            if self.bars_in_the_same_direction >= bars_in_same_direction:
                self.current_direction *= -1
                self.bars_in_the_same_direction = 0

            self.bars_in_the_same_direction += 1

            # Add Left bar.
            if self.current_direction < 0:
                leds_to_show = min(steps, bar_length)

                left_index = (self.output_left_length - steps)
                right_index = (self.output_left_length - (steps - leds_to_show))

                current_output_left[0][left_index:right_index] = current_color_for_bar[0]
                current_output_left[1][left_index:right_index] = current_color_for_bar[1]
                current_output_left[2][left_index:right_index] = current_color_for_bar[2]

                self.current_bar_length_left = leds_to_show

            # Add Right bar.
            else:
                leds_to_show = min(steps, bar_length)

                left_index = (steps - leds_to_show) - 1
                left_index = max(left_index, 0)
                right_index = steps

                current_output_right[0][left_index:right_index] = current_color_for_bar[0]
                current_output_right[1][left_index:right_index] = current_color_for_bar[1]
                current_output_right[2][left_index:right_index] = current_color_for_bar[2]

                self.current_bar_length_right = leds_to_show

        # Build output array.
        output[0][:self.output_left_max_index] = current_output_left[0]
        output[1][:self.output_left_max_index] = current_output_left[1]
        output[2][:self.output_left_max_index] = current_output_left[2]

        output[0][self.output_right_min_index:] = current_output_right[0]
        output[1][self.output_right_min_index:] = current_output_right[1]
        output[2][self.output_right_min_index:] = current_output_right[2]

        self.queue_output_array_noneblocking(output)

        self.output_left = current_output_left
        self.output_right = current_output_right
