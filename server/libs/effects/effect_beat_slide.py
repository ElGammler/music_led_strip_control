import numpy as np

from libs.effects.effect import Effect


class EffectBeatSlide(Effect):
    def __init__(self, device) -> None:
        # Call the constructor of the base class.
        super().__init__(device)
        self.current_position = 0

    def run(self):
        effect_config = self.get_effect_config("effect_beat_slide")
        led_count = self._device.device_config["led_count"]

        audio_data = self.get_audio_data()
        y = self.get_mel(audio_data)

        if y is None:
            return

        self.update_freq_channels(y)
        self.detect_freqs()

        self.current_color = self._color_service.colour(effect_config["color"])

        # Build an empty array.
        output = np.zeros((3, led_count))

        # Calculate how many steps the array will roll.
        steps = self.get_roll_steps(effect_config["speed"])

        self.current_position += steps
        if self.current_position > led_count:
            self.current_position = 0

        start_position = self.current_position
        end_position = start_position - effect_config["bar_length"]
        end_position = max(end_position, 0)

        output = (self.prev_output * effect_config["decay"]).astype(int)

        if self.current_freq_detects["beat"]:
            start_position += effect_config["slider_length"]
            start_position = min(led_count, start_position)

            self.current_position = start_position

        output[0][end_position:start_position] = self.current_color[0]
        output[1][end_position:start_position] = self.current_color[1]
        output[2][end_position:start_position] = self.current_color[2]

        self.prev_output = output
        self.queue_output_array_noneblocking(output)
