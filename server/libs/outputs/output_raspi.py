import numpy as np
from loguru import logger

from libs.outputs.output import Output  # pylint: disable=E0611, E0401


class OutputRaspi(Output):
    def __init__(self, device) -> None:
        # Call the constructor of the base class.
        super().__init__(device)

        try:
            import _rpi_ws281x as ws  # pylint: disable=import-error
        except (ImportError, ModuleNotFoundError):
            return
            from rpi_ws281x import ws

        output_id = "output_raspi"

        # LED strip configuration:
        self._led_count = int(self._device_config["led_count"])                                 # Number of LED pixels.
        self._led_pin = int(self._device_config["output"][output_id]["led_pin"])                # GPIO pin connected to the pixels (18 uses PWM!).
        self._led_freq_hz = int(self._device_config["output"][output_id]["led_freq_hz"])        # LED signal frequency in hertz (usually 800khz).
        self._led_dma = int(self._device_config["output"][output_id]["led_dma"])                # DMA channel to use for generating signal (try 10).
        self._led_brightness = int(self._device_config["led_brightness"])  # Set to '0' for darkest and 100 for brightest.
        self._led_invert = int(self._device_config["output"][output_id]["led_invert"])          # Set to 'True' to invert the signal (when using NPN transistor level shift).
        self._led_channel = int(self._device_config["output"][output_id]["led_channel"])        # set to '1' for GPIOs 13, 19, 41, 45 or 53.
        self._led_strip = self._device_config["led_strip"]

        # Set Fallback Strip
        self._led_strip_translated = ws.WS2811_STRIP_RGB

        self._led_strip_mapper = {
            "sk6812_strip_rgbw": ws.SK6812_STRIP_RGBW,
            "sk6812_strip_rbgw": ws.SK6812_STRIP_RBGW,
            "sk6812_strip_grbw": ws.SK6812_STRIP_GRBW,
            "sk6812_strip_gbrw": ws.SK6812_STRIP_GBRW,
            "sk6812_strip_brgw": ws.SK6812_STRIP_BRGW,
            "sk6812_strip_bgrw": ws.SK6812_STRIP_BGRW,
            "sk6812_shift_wmask": ws.SK6812_SHIFT_WMASK,
            "ws2811_strip_rgb": ws.WS2811_STRIP_RGB,
            "ws2811_strip_rbg": ws.WS2811_STRIP_RBG,
            "ws2811_strip_grb": ws.WS2811_STRIP_GRB,
            "ws2811_strip_gbr": ws.WS2811_STRIP_GBR,
            "ws2811_strip_brg": ws.WS2811_STRIP_BRG,
            "ws2811_strip_bgr": ws.WS2811_STRIP_BGR,
            "ws2812_strip": ws.WS2812_STRIP,
            "sk6812_strip": ws.SK6812_STRIP,
            "sk6812w_strip": ws.SK6812W_STRIP
        }

        try:
            led_strip = self._led_strip_mapper[self._led_strip]
            if led_strip is not None:
                self._led_strip_translated = led_strip
                logger.debug(f"Found Led Strip {self._led_strip}")
        except Exception as e:
            logger.exception(f"Could not find LED Strip Type. Exception: {str(e)}")

        self._led_brightness_translated = int(255 * (self._led_brightness / 100))

        logger.debug(f"LED Brightness: {self._led_brightness}")
        logger.debug(f"LED Brightness converted: {self._led_brightness_translated}")

        self._leds = ws.new_ws2811_t()

        self.channel = ws.ws2811_channel_get(self._leds, self._led_channel)

        ws.ws2811_channel_t_strip_type_set(self.channel, self._led_strip_translated)
        ws.ws2811_channel_t_count_set(self.channel, self._led_count)
        ws.ws2811_channel_t_gpionum_set(self.channel, self._led_pin)
        ws.ws2811_channel_t_invert_set(self.channel, self._led_invert)
        ws.ws2811_channel_t_brightness_set(self.channel, self._led_brightness_translated)

        ws.ws2811_t_freq_set(self._leds, self._led_freq_hz)
        ws.ws2811_t_dmanum_set(self._leds, self._led_dma)

        # Initialize library with LED configuration.
        resp = ws.ws2811_init(self._leds)
        if resp != ws.WS2811_SUCCESS:
            message = ws.ws2811_get_return_t_str(resp)
            raise RuntimeError(f"ws2811_init failed with code {resp} ({message})")

    def show(self, output_array):
        try:
            import _rpi_ws281x as ws  # pylint: disable=import-error
        except (ImportError, ModuleNotFoundError):
            from rpi_ws281x import ws

        # Typecast the array to int.
        output_array = output_array.clip(0, 255).astype(int)

        # Check if we have a white channel or not.
        if len(output_array[:]) == 4 and "SK6812" in self._led_strip:
            # Sort the colors as RGB type.
            g = np.left_shift(output_array[1][:].astype(int), 24)  # pylint: disable=assignment-from-no-return
            r = np.left_shift(output_array[0][:].astype(int), 16)  # pylint: disable=assignment-from-no-return
            b = np.left_shift(output_array[2][:].astype(int), 8)  # pylint: disable=assignment-from-no-return
            w = output_array[3][:].astype(int)
            grbw = np.bitwise_or(np.bitwise_or(np.bitwise_or(r, g), b), w).astype(int)

            # You can only use ws2811_leds_set with the custom version.
            for i in range(self._led_count):
                ws.ws2811_led_set(self.channel, i, int(grbw[i].item()))
        else:
            # Sort the colors as RGB type.
            g = np.left_shift(output_array[1][:].astype(int), 16)  # pylint: disable=assignment-from-no-return
            r = np.left_shift(output_array[0][:].astype(int), 8)  # pylint: disable=assignment-from-no-return
            b = output_array[2][:].astype(int)
            grb = np.bitwise_or(np.bitwise_or(r, g), b).astype(int)

            # You can only use ws2811_leds_set with the custom version.
            for i in range(self._led_count):
                ws.ws2811_led_set(self.channel, i, grb[i].item())

        resp = ws.ws2811_render(self._leds)

        if resp != ws.WS2811_SUCCESS:
            message = ws.ws2811_get_return_t_str(resp)
            raise RuntimeError(f"ws2811_render failed with code {resp} ({message})")
