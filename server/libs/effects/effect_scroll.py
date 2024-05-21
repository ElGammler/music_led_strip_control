import numpy as np
from scipy.ndimage import gaussian_filter1d

from libs.effects.effect import Effect  # pylint: disable=E0611, E0401


class EffectScroll(Effect):
    def __init__(self, device) -> None:
        # Call the constructor of the base class.
        super().__init__(device)

        # Scroll Variables.
        self.output_scroll_high = np.array([[0 for i in range(self.led_count)] for i in range(3)])
        self.output_scroll_mid = np.array([[0 for i in range(self.led_count)] for i in range(3)])
        self.output_scroll_low = np.array([[0 for i in range(self.led_count)] for i in range(3)])

    def run(self):
        effect_config = self.get_effect_config("effect_scroll")
        led_count = self._device.device_config["led_count"]
        led_mid = self._device.device_config["led_mid"]

        audio_data = self.get_audio_data()
        y = self.get_mel(audio_data)

        if y is None:
            return

        # Effect that scrolls colors corresponding to frequencies across the strip.
        y **= 4.0
        n_pixels = led_count
        y = np.copy(self._math_service.interpolate(y, (n_pixels // 2)))
        self._dsp.common_mode.update(y)
        self.prev_spectrum = np.copy(y)

        y = np.clip(y, 0, 1)
        lows = y[:len(y) // 6]
        mids = y[len(y) // 6: 2 * len(y) // 5]
        high = y[2 * len(y) // 5:]
        # Max values.
        lows_max = float(np.max(lows)) * effect_config["lows_multiplier"]
        mids_max = float(np.max(mids)) * effect_config["mids_multiplier"]
        high_max = float(np.max(high)) * effect_config["high_multiplier"]
        # Indexes of max values.
        # Map to color gradient.
        lows_val = (np.array(self._color_service.colour(effect_config["lows_color"])) * lows_max).astype(int)
        mids_val = (np.array(self._color_service.colour(effect_config["mids_color"])) * mids_max).astype(int)
        high_val = (np.array(self._color_service.colour(effect_config["high_color"])) * high_max).astype(int)
        # Scrolling effect window.

        # Calculate how many steps the array will roll.
        high_steps = effect_config["high_speed"]
        mid_steps = effect_config["mid_speed"]
        low_steps = effect_config["low_speed"]

        if (high_steps > 0):
            self.output_scroll_high[:, high_steps:] = self.output_scroll_high[:, :-high_steps]

            # Create new color originating at the center.
            self.output_scroll_high[0, :high_steps] = high_val[0]
            self.output_scroll_high[1, :high_steps] = high_val[1]
            self.output_scroll_high[2, :high_steps] = high_val[2]

        if (mid_steps > 0):
            self.output_scroll_mid[:, mid_steps:] = self.output_scroll_mid[:, :-mid_steps]

            # Create new color originating at the center.
            self.output_scroll_mid[0, :mid_steps] = mids_val[0]
            self.output_scroll_mid[1, :mid_steps] = mids_val[1]
            self.output_scroll_mid[2, :mid_steps] = mids_val[2]

        if (low_steps > 0):
            self.output_scroll_low[:, low_steps:] = self.output_scroll_low[:, :-low_steps]

            # Create new color originating at the center.
            self.output_scroll_low[0, :low_steps] = lows_val[0]
            self.output_scroll_low[1, :low_steps] = lows_val[1]
            self.output_scroll_low[2, :low_steps] = lows_val[2]

        self.output[0] = self.output_scroll_high[0] + self.output_scroll_mid[0] + self.output_scroll_low[0]
        self.output[1] = self.output_scroll_high[1] + self.output_scroll_mid[1] + self.output_scroll_low[1]
        self.output[2] = self.output_scroll_high[2] + self.output_scroll_mid[2] + self.output_scroll_low[2]

        # Decay the history arrays for the next round
        decay = effect_config["decay"] / 100
        self.output_scroll_high = (self.output_scroll_high * decay).astype(int)
        self.output_scroll_mid = (self.output_scroll_mid * decay).astype(int)
        self.output_scroll_low = (self.output_scroll_low * decay).astype(int)

        blur_amount = effect_config["blur"]
        if blur_amount > 0:
            self.output = gaussian_filter1d(self.output, sigma=blur_amount)

        output_array = self.mirror_array(self.output, led_mid, led_count) if effect_config["mirror"] else self.output

        self.queue_output_array_noneblocking(output_array)
