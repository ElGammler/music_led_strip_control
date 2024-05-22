import numpy as np
from scipy.ndimage import gaussian_filter1d

from libs.effects.effect import Effect


class EffectAdvancedScroll(Effect):
    def __init__(self, device) -> None:
        # Call the constructor of the base class.
        super().__init__(device)

        # Scroll Variables.
        self.output_scroll_subbass = np.array([[0 for i in range(self.led_count)] for i in range(3)])
        self.output_scroll_bass = np.array([[0 for i in range(self.led_count)] for i in range(3)])
        self.output_scroll_lowmid = np.array([[0 for i in range(self.led_count)] for i in range(3)])
        self.output_scroll_mid = np.array([[0 for i in range(self.led_count)] for i in range(3)])
        self.output_scroll_uppermid = np.array([[0 for i in range(self.led_count)] for i in range(3)])
        self.output_scroll_presence = np.array([[0 for i in range(self.led_count)] for i in range(3)])
        self.output_scroll_brilliance = np.array([[0 for i in range(self.led_count)] for i in range(3)])

    def run(self):
        effect_config = self.get_effect_config("effect_advanced_scroll")
        led_count = self._device.device_config["led_count"]
        led_mid = self._device.device_config["led_mid"]

        audio_data = self.get_audio_data()
        y = self.get_mel(audio_data)

        if y is None:
            return

        # Effect that scrolls colors corresponding to frequencies across the strip.
        # Increase the peaks by y^4
        y **= 4.0
        n_pixels = led_count

        self.prev_spectrum = np.copy(y)

        y = np.clip(y, 0, 1)

        subbass = y[:int(len(y) * (1 / 24))]
        bass = y[int(len(y) * (1 / 24)):int(len(y) * (2 / 24))]
        lowmid = y[int(len(y) * (2 / 24)):int(len(y) * (5 / 24))]
        mid = y[int(len(y) * (5 / 24)):int(len(y) * (12 / 24))]
        uppermid = y[int(len(y) * (12 / 24)):int(len(y) * (16 / 24))]
        presence = y[int(len(y) * (16 / 24)):int(len(y) * (19 / 24))]
        brilliance = y[int(len(y) * (19 / 24)):]

        # Max values
        subbass_max = float(np.max(subbass)) * effect_config["subbass_multiplier"]
        bass_max = float(np.max(bass)) * effect_config["bass_multiplier"]
        lowmid_max = float(np.max(lowmid)) * effect_config["lowmid_multiplier"]
        mid_max = float(np.max(mid)) * effect_config["mid_multiplier"]
        uppermid_max = float(np.max(uppermid)) * effect_config["uppermid_multiplier"]
        presence_max = float(np.max(presence)) * effect_config["presence_multiplier"]
        brilliance_max = float(np.max(brilliance)) * effect_config["brilliance_multiplier"]

        # Indices of max values.
        # Map to color gradient.
        subbass_val = (np.array(self._color_service.colour(effect_config["subbass_color"])) * subbass_max).astype(int)
        bass_val = (np.array(self._color_service.colour(effect_config["bass_color"])) * bass_max).astype(int)
        lowmid_val = (np.array(self._color_service.colour(effect_config["lowmid_color"])) * lowmid_max).astype(int)
        mid_val = (np.array(self._color_service.colour(effect_config["mid_color"])) * mid_max).astype(int)
        uppermid_val = (np.array(self._color_service.colour(effect_config["uppermid_color"])) * uppermid_max).astype(int)
        presence_val = (np.array(self._color_service.colour(effect_config["presence_color"])) * presence_max).astype(int)
        brilliance_val = (np.array(self._color_service.colour(effect_config["brilliance_color"])) * brilliance_max).astype(int)

        # Calculate how many steps the array will roll.
        subbass_steps = effect_config["subbass_speed"]
        bass_steps = effect_config["bass_speed"]
        lowmid_steps = effect_config["lowmid_speed"]
        mid_steps = effect_config["mid_speed"]
        uppermid_steps = effect_config["uppermid_speed"]
        presence_steps = effect_config["presence_speed"]
        brilliance_steps = effect_config["brilliance_speed"]

        if (subbass_steps > 0):
            self.output_scroll_subbass[:, subbass_steps:] = self.output_scroll_subbass[:, :-subbass_steps]

            # Create new color originating at the center.
            self.output_scroll_subbass[0, :subbass_steps] = subbass_val[0]
            self.output_scroll_subbass[1, :subbass_steps] = subbass_val[1]
            self.output_scroll_subbass[2, :subbass_steps] = subbass_val[2]

        if (bass_steps > 0):
            self.output_scroll_bass[:, bass_steps:] = self.output_scroll_bass[:, :-bass_steps]

            # Create new color originating at the center.
            self.output_scroll_bass[0, :bass_steps] = bass_val[0]
            self.output_scroll_bass[1, :bass_steps] = bass_val[1]
            self.output_scroll_bass[2, :bass_steps] = bass_val[2]

        if (lowmid_steps > 0):
            self.output_scroll_lowmid[:, lowmid_steps:] = self.output_scroll_lowmid[:, :-lowmid_steps]

            # Create new color originating at the center.
            self.output_scroll_lowmid[0, :lowmid_steps] = lowmid_val[0]
            self.output_scroll_lowmid[1, :lowmid_steps] = lowmid_val[1]
            self.output_scroll_lowmid[2, :lowmid_steps] = lowmid_val[2]

        if (mid_steps > 0):
            self.output_scroll_mid[:, mid_steps:] = self.output_scroll_mid[:, :-mid_steps]

            # Create new color originating at the center.
            self.output_scroll_mid[0, :mid_steps] = mid_val[0]
            self.output_scroll_mid[1, :mid_steps] = mid_val[1]
            self.output_scroll_mid[2, :mid_steps] = mid_val[2]

        if (uppermid_steps > 0):
            self.output_scroll_uppermid[:, uppermid_steps:] = self.output_scroll_uppermid[:, :-uppermid_steps]

            # Create new color originating at the center.
            self.output_scroll_uppermid[0, :uppermid_steps] = uppermid_val[0]
            self.output_scroll_uppermid[1, :uppermid_steps] = uppermid_val[1]
            self.output_scroll_uppermid[2, :uppermid_steps] = uppermid_val[2]

        if (presence_steps > 0):
            self.output_scroll_presence[:, presence_steps:] = self.output_scroll_presence[:, :-presence_steps]

            # Create new color originating at the center.
            self.output_scroll_presence[0, :presence_steps] = presence_val[0]
            self.output_scroll_presence[1, :presence_steps] = presence_val[1]
            self.output_scroll_presence[2, :presence_steps] = presence_val[2]

        if (brilliance_steps > 0):
            self.output_scroll_brilliance[:, brilliance_steps:] = self.output_scroll_brilliance[:, :-brilliance_steps]

            # Create new color originating at the center.
            self.output_scroll_brilliance[0, :brilliance_steps] = brilliance_val[0]
            self.output_scroll_brilliance[1, :brilliance_steps] = brilliance_val[1]
            self.output_scroll_brilliance[2, :brilliance_steps] = brilliance_val[2]

        self.output[0] = self.output_scroll_subbass[0] + self.output_scroll_bass[0] + self.output_scroll_lowmid[0] + self.output_scroll_mid[0] + self.output_scroll_uppermid[0] + self.output_scroll_presence[0] + self.output_scroll_brilliance[0]
        self.output[1] = self.output_scroll_subbass[1] + self.output_scroll_bass[1] + self.output_scroll_lowmid[1] + self.output_scroll_mid[1] + self.output_scroll_uppermid[1] + self.output_scroll_presence[1] + self.output_scroll_brilliance[1]
        self.output[2] = self.output_scroll_subbass[2] + self.output_scroll_bass[2] + self.output_scroll_lowmid[2] + self.output_scroll_mid[2] + self.output_scroll_uppermid[2] + self.output_scroll_presence[2] + self.output_scroll_brilliance[2]

        # Decay the history arrays for the next round
        decay = effect_config["decay"] / 100
        self.output_scroll_subbass = (self.output_scroll_subbass * decay).astype(int)
        self.output_scroll_bass = (self.output_scroll_bass * decay).astype(int)
        self.output_scroll_lowmid = (self.output_scroll_lowmid * decay).astype(int)
        self.output_scroll_mid = (self.output_scroll_mid * decay).astype(int)
        self.output_scroll_uppermid = (self.output_scroll_uppermid * decay).astype(int)
        self.output_scroll_presence = (self.output_scroll_presence * decay).astype(int)
        self.output_scroll_brilliance = (self.output_scroll_brilliance * decay).astype(int)

        blur_amount = effect_config["blur"]
        if blur_amount > 0:
            self.output = gaussian_filter1d(self.output, sigma=blur_amount)

        output_array = self.mirror_array(self.output, led_mid, led_count) if effect_config["mirror"] else self.output

        self.queue_output_array_noneblocking(output_array)
