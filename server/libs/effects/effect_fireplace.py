from random import randint

import numpy as np
from scipy.ndimage import gaussian_filter1d

from libs.effects.effect import Effect  # pylint: disable=E0611, E0401


class EffectFireplace(Effect):

    def __init__(self, device) -> None:
        # Call the constructor of the base class.
        super().__init__(device)
        # Setup for "EffectFireplace" (don't change this).

        self.sparks_area_current_length = 0
        self.sparks_area_target_length = 0
        self.sparks_target_appear_distance = 0
        self.sparks_current_appear_distance = 0

        self.sparks_target_new_sparks_length = 0
        self.sparks_new_sparks_distance = 0
        self.sparks_flicker_speed_counter = 0
        self.sparks_fly_speed_counter = 0

        self.sparks_array = np.zeros((3, self._device.device_config["led_count"]))

        self.firebase_area_current_length = 0
        self.firebase_area_target_length = 0
        self.firebase_flicker_speed_counter = 0

        self.current_variation_spark_color = [0, 0, 0]

    def run(self):
        #
        #
        #  |     firebase_area      |                      sparks_area                          |                           |
        #  |----*---*-------*-----*-    *       *                 *     *                *                                  |
        #

        # Get the config of the current effect.
        effect_config = self.get_effect_config("effect_fireplace")

        led_count = self._device.device_config["led_count"]
        led_mid = self._device.device_config["led_mid"]

        # Build an empty array.
        output_array = np.zeros((3, led_count))

        firebase_flicker_speed = effect_config["firebase_flicker_speed"]
        firebase_area_maxlength = effect_config["firebase_area_maxlength"]
        firebase_area_minlength = effect_config["firebase_area_minlength"]
        firebase_area_minlength = min(firebase_area_minlength, firebase_area_maxlength)

        sparks_flicker_speed = effect_config["sparks_flicker_speed"]
        sparks_fly_speed = effect_config["sparks_fly_speed"]

        sparks_maxappear_distance = effect_config["sparks_maxappear_distance"]
        sparks_minappear_distance = effect_config["sparks_minappear_distance"]
        sparks_minappear_distance = min(sparks_minappear_distance, sparks_maxappear_distance)

        sparks_max_length = effect_config["sparks_max_length"]
        sparks_min_length = effect_config["sparks_min_length"]
        sparks_min_length = min(sparks_min_length, sparks_max_length)

        sparks_area_minlength = effect_config["sparks_area_minlength"]
        sparks_area_maxlength = effect_config["sparks_area_maxlength"]
        sparks_area_minlength = min(sparks_area_minlength, sparks_area_maxlength)

        use_color_variation = effect_config["use_color_variation"]
        color_variation = effect_config["color_variation"]

        blur = effect_config["blur"]
        mask_blur = effect_config["mask_blur"]

        firebase_maincolor = self._config_colours[effect_config["firebase_maincolor"]]
        sparks_maincolor = self._config_colours[effect_config["sparks_maincolor"]]

        # Calculate the target area lengths.
        if self.firebase_area_target_length in {0, self.firebase_area_current_length}:
            self.firebase_area_target_length = randint(firebase_area_minlength, firebase_area_maxlength)

        if self.sparks_area_target_length in {0, self.sparks_area_current_length}:
            self.sparks_area_target_length = randint(sparks_area_minlength, sparks_area_maxlength)

        # Get the flickering speed of the sparks and the firebase.
        firebase_steps = self.get_firebase_flicker_steps(firebase_flicker_speed)
        sparks_steps = self.get_sparks_flicker_steps(sparks_flicker_speed)

        # enlagre the flyspeed to randomize 0.x values
        sparks_enlarged_fly_speed = int(sparks_fly_speed * 100)
        sparks_enlarged_fly_speed_randomized = randint(sparks_enlarged_fly_speed, sparks_enlarged_fly_speed + int(sparks_enlarged_fly_speed * 0.2))
        sparks_fly_speed_randomized = sparks_enlarged_fly_speed_randomized / 100
        sparks_fly_steps = self.get_sparks_fly_steps(sparks_fly_speed_randomized)

        # Init firebase.s
        firebase_array = np.zeros((3, led_count))

        # Calculate the new current length of the areas.
        self.firebase_area_current_length = self.get_current_length(self.firebase_area_current_length, firebase_steps, self.firebase_area_target_length)

        # Set the main color of the firebase.
        firebase_array[0][:self.firebase_area_current_length] = firebase_maincolor[0]
        firebase_array[1][:self.firebase_area_current_length] = firebase_maincolor[1]
        firebase_array[2][:self.firebase_area_current_length] = firebase_maincolor[2]

        if sparks_fly_steps > 0:

            self.sparks_area_current_length = self.get_current_length(self.sparks_area_current_length, sparks_steps, self.sparks_area_target_length)

            #
            #                  sparks_target_appear_distance
            #   |                           |                                       |
            #   |                           |                                       |
            #   |   ****************                                                |
            #   |               ******************                                  |
            #   |                           ******************                      |
            #   |***                           ******************                   |
            #   |                              |                                    |
            #   |                              |                                    |
            #                               sparks_current_appear_distance

            # Check if we need to calculate a new spark.
            if self.sparks_target_appear_distance == 0 or (self.sparks_current_appear_distance - self.sparks_target_appear_distance) >= self.sparks_target_appear_distance:
                self.sparks_target_new_sparks_length = randint(sparks_min_length, sparks_max_length)
                self.sparks_current_appear_distance = 0
                self.sparks_target_appear_distance = randint(sparks_minappear_distance, sparks_maxappear_distance)

                self.current_variation_spark_color = self.get_variation_color(sparks_maincolor, color_variation)

            # Rotate the array.
            self.sparks_array[:, sparks_fly_steps:] = self.sparks_array[:, :-sparks_fly_steps]
            self.sparks_array[:, :sparks_fly_steps][0] = 0
            self.sparks_array[:, :sparks_fly_steps][1] = 0
            self.sparks_array[:, :sparks_fly_steps][2] = 0

            self.sparks_current_appear_distance += sparks_fly_steps

            # Reached the target distance.
            if self.sparks_current_appear_distance >= self.sparks_target_appear_distance:

                distance_diff = self.sparks_current_appear_distance - self.sparks_target_appear_distance

                offset = 0
                if distance_diff > self.sparks_target_new_sparks_length:
                    offset = distance_diff - self.sparks_target_new_sparks_length

                if use_color_variation:
                    self.sparks_array[0][offset:sparks_fly_steps] = self.current_variation_spark_color[0]
                    self.sparks_array[1][offset:sparks_fly_steps] = self.current_variation_spark_color[1]
                    self.sparks_array[2][offset:sparks_fly_steps] = self.current_variation_spark_color[2]
                else:
                    self.sparks_array[0][offset:sparks_fly_steps] = sparks_maincolor[0]
                    self.sparks_array[1][offset:sparks_fly_steps] = sparks_maincolor[1]
                    self.sparks_array[2][offset:sparks_fly_steps] = sparks_maincolor[2]

        spars_array_cutted = np.zeros((3, led_count))
        spars_array_cutted[0][:self.sparks_area_current_length] = self.sparks_array[0][:self.sparks_area_current_length]
        spars_array_cutted[1][:self.sparks_area_current_length] = self.sparks_array[1][:self.sparks_area_current_length]
        spars_array_cutted[2][:self.sparks_area_current_length] = self.sparks_array[2][:self.sparks_area_current_length]

        # Get the mask array to smooth out the edges
        mask_array = self.get_mask_array(led_count, mask_blur)

        overlay_array = np.where(spars_array_cutted != 0, spars_array_cutted, firebase_array)
        overlay_array *= mask_array / 100

        output_array = gaussian_filter1d(overlay_array, sigma=blur) if blur != 0 else overlay_array

        if effect_config["swap_side"]:
            output_array[:, ::] = output_array[:, ::-1]

        if effect_config["mirror"]:
            output_array = self.mirror_array(output_array, led_mid, led_count)

        # Add the output array to the queue.
        self.queue_output_array_blocking(output_array)

    @staticmethod
    def get_current_length(current_length, steps, target_length) -> int:

        if current_length == target_length:
            return current_length

        # Increase current length.
        if current_length <= target_length:
            current_length += steps

            # If new current length is longer than the target, set the target length.
            current_length = min(current_length, target_length)
        else:
            # Decrease current length.
            current_length -= steps
            current_length = max(current_length, target_length)

        return current_length

    def get_mask_array(self, led_count, mask_blur):
        mask_array = np.zeros((3, led_count))
        mask_array[0][:self.sparks_area_current_length] = 100
        mask_array[1][:self.sparks_area_current_length] = 100
        mask_array[2][:self.sparks_area_current_length] = 100

        mask_array[0][self.firebase_area_current_length - 5:self.firebase_area_current_length + 5] = 0
        mask_array[1][self.firebase_area_current_length - 5:self.firebase_area_current_length + 5] = 0
        mask_array[2][self.firebase_area_current_length - 5:self.firebase_area_current_length + 5] = 0

        one_half_spark_area = self.sparks_area_current_length

        fade_out = np.zeros((3, one_half_spark_area))
        fade_out[0] = np.linspace(50, 0, one_half_spark_area, endpoint=True)
        fade_out[1] = np.linspace(50, 0, one_half_spark_area, endpoint=True)
        fade_out[2] = np.linspace(50, 0, one_half_spark_area, endpoint=True)

        fade_out_end_cut = len(mask_array[0]) - (self.sparks_area_current_length - one_half_spark_area)
        fade_out_end_index = min(one_half_spark_area, fade_out_end_cut)

        fade_out_end_index = max(fade_out_end_index, 0)

        mask_array[0][self.sparks_area_current_length - one_half_spark_area:self.sparks_area_current_length] = fade_out[0][:fade_out_end_index]
        mask_array[1][self.sparks_area_current_length - one_half_spark_area:self.sparks_area_current_length] = fade_out[1][:fade_out_end_index]
        mask_array[2][self.sparks_area_current_length - one_half_spark_area:self.sparks_area_current_length] = fade_out[2][:fade_out_end_index]

        if mask_blur != 0:
            mask_array = gaussian_filter1d(mask_array, sigma=mask_blur)
        return mask_array

    @staticmethod
    def get_variation_color(main_color, color_variation) -> list[int]:
        red_min = main_color[0] - color_variation
        red_max = main_color[0] + color_variation
        red_min = max(red_min, 0)

        red_max = min(red_max, 255)

        green_min = main_color[1] - color_variation
        green_max = main_color[1] + color_variation
        green_min = max(green_min, 0)

        green_max = min(green_max, 255)

        blue_min = main_color[2] - color_variation
        blue_max = main_color[2] + color_variation
        blue_min = max(blue_min, 0)

        blue_max = min(blue_max, 255)

        result_color = [0, 0, 0]
        result_color[0] = randint(red_min, red_max)
        result_color[1] = randint(green_min, green_max)
        result_color[2] = randint(blue_min, blue_max)

        return result_color

    def get_firebase_flicker_steps(self, current_speed):
        """Calculate the steps for the rollspeed.

        Up to 1 you can adjust the speed very fine. After this, you need to add decades to increase the speed.
        """
        max_counter = 1
        steps = 0
        self.firebase_flicker_speed_counter += current_speed

        if self.firebase_flicker_speed_counter > max_counter:
            self.firebase_flicker_speed_counter = 0

            steps = int(1 / (max_counter / current_speed)) if max_counter / current_speed < 1 else 1

        else:
            steps = 0

        return steps

    def get_sparks_flicker_steps(self, current_speed):
        """Calculate the steps for the rollspeed.

        Up to 1 you can adjust the speed very fine. After this, you need to add decades to increase the speed.
        """
        max_counter = 1
        steps = 0
        self.sparks_flicker_speed_counter += current_speed

        if self.sparks_flicker_speed_counter > max_counter:
            self.sparks_flicker_speed_counter = 0

            steps = int(1 / (max_counter / current_speed)) if max_counter / current_speed < 1 else 1

        else:
            steps = 0

        return steps

    def get_sparks_fly_steps(self, current_speed):
        """Calculate the steps for the rollspeed.

        Up to 1 you can adjust the speed very fine. After this, you need to add decades to increase the speed.
        """
        max_counter = 1
        steps = 0
        self.sparks_fly_speed_counter += current_speed

        if self.sparks_fly_speed_counter > max_counter:
            self.sparks_fly_speed_counter = 0

            steps = int(1 / (max_counter / current_speed)) if max_counter / current_speed < 1 else 1

        else:
            steps = 0

        return steps
