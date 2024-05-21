import numpy as np

from libs.effects.effect import Effect  # pylint: disable=E0611, E0401


class EffectSegmentColor(Effect):
    def run(self):
        """Show one single color."""
        # Get the config of the current effect.
        effect_config = self.get_effect_config("effect_segment_color")
        led_count = self._device.device_config["led_count"]
        # Build an empty array.
        output_array = np.zeros((3, led_count))

        max_len = (len(effect_config.keys()) // 3) + 1

        for x in range(1, max_len):
            segment_number = str(x).zfill(2)

            colorkey = f"segment_{segment_number}_color"
            startkey = f"segment_{segment_number}_start"
            endkey = f"segment_{segment_number}_end"

            if (colorkey not in effect_config) or (startkey not in effect_config) or (endkey not in effect_config):
                continue

            start = effect_config[startkey]
            end = effect_config[endkey]

            if start == 0 and end == 0:
                continue

            if start <= 0:
                start = 1

            start = min(start, led_count)

            if end <= 0:
                end = 1

            end = min(end, led_count)

            if end < start:
                continue

            start_translated = start - 1
            end_translated = end

            color = self._config_colours[effect_config[colorkey]]
            output_array[0][start_translated:end_translated] = color[0]
            output_array[1][start_translated:end_translated] = color[1]
            output_array[2][start_translated:end_translated] = color[2]

        # Add the output array to the queue.
        self.queue_output_array_blocking(output_array)
