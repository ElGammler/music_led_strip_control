import numpy as np

from libs.effects.effect import Effect  # pylint: disable=E0611, E0401


class EffectVuMeter(Effect):
    def __init__(self, device) -> None:

        # Call the constructor of the base class.
        super().__init__(device)

        # Setup for "VU Meter" (don't change these).
        self.max_vol = 0
        self.vol_history = np.zeros(300)

    def run(self):
        """Effect that lights up more leds when volume gets higher."""
        effect_config = self.get_effect_config("effect_vu_meter")
        led_count = self._device.device_config["led_count"]

        audio_data = self.get_audio_data()
        vol = self.get_vol(audio_data)

        if vol is None:
            return

        self.set_vol_history(vol)
        normalized_vol = self.get_normalized_vol(vol)

        # Build an empty array.
        output = np.zeros((3, led_count))

        use_gradient = effect_config["use_gradient"]
        current_gradient = effect_config["gradient"]

        leds_on = int(normalized_vol * led_count)

        if use_gradient:
            full_gradient_ref = self._color_service.full_gradients

            output[0][: leds_on] = full_gradient_ref[current_gradient][0][:leds_on]
            output[1][: leds_on] = full_gradient_ref[current_gradient][1][:leds_on]
            output[2][: leds_on] = full_gradient_ref[current_gradient][2][:leds_on]
        else:

            output[0][: leds_on] = self._color_service.colour(effect_config["color"])[0]
            output[1][: leds_on] = self._color_service.colour(effect_config["color"])[1]
            output[2][: leds_on] = self._color_service.colour(effect_config["color"])[2]

        self.max_vol = max(normalized_vol, self.max_vol)

        # Show the max. volume
        output[0][int(self.max_vol * led_count) - effect_config["bar_length"]: int(self.max_vol * led_count)] = self._color_service.colour(effect_config["max_vol_color"])[0]
        output[1][int(self.max_vol * led_count) - effect_config["bar_length"]: int(self.max_vol * led_count)] = self._color_service.colour(effect_config["max_vol_color"])[1]
        output[2][int(self.max_vol * led_count) - effect_config["bar_length"]: int(self.max_vol * led_count)] = self._color_service.colour(effect_config["max_vol_color"])[2]

        self.max_vol -= effect_config["speed"] / 10000

        self.queue_output_array_noneblocking(output)

        self.prev_output = output

    def set_vol_history(self, current_vol):
        # Roll the history for one.
        self.vol_history = np.roll(self.vol_history, 1, axis=0)
        # Add the new value.
        self.vol_history[0] = current_vol

    def get_normalized_vol(self, current_vol):
        return (current_vol - np.min(self.vol_history)) / (np.max(self.vol_history) - np.min(self.vol_history))
