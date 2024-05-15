import socket

import numpy as np
from loguru import logger

from libs.outputs.output import Output  # pylint: disable=E0611, E0401


class OutputUDP(Output):
    def __init__(self, device) -> None:
        # Call the constructor of the base class.
        super().__init__(device)
        output_id = "output_udp"

        self._udp_client_ip = self._device_config["output"][output_id]["udp_client_ip"]
        self._udp_client_port = int(self._device_config["output"][output_id]["udp_client_port"])
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._led_strip = self._device_config["led_strip"]
        self._led_brightness = int(self._device_config["led_brightness"])  # Set to '0' for darkest and 100 for brightest.

    def show(self, output_array):

        output_array = output_array * (self._led_brightness / 100)

        output_array = self.map_channels(output_array)
        # Typecast the array to int.
        output_array = output_array.clip(0, 255).astype(np.uint8)

        byte_array = output_array.tobytes("F")
        try:
            self._sock.sendto(byte_array, (self._udp_client_ip, self._udp_client_port))
        except Exception as ex:
            logger.exception(f"Could not send to client: {ex}")
            logger.debug(f"Reinit output of {self._udp_client_ip}")
            self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def map_channels(self, output_array_in):
        if "sk6812" in self._led_strip:
            if len(output_array_in[:]) == 4:
                return self.map_four_channels_sk(output_array_in)
            return self.map_three_channels_sk(output_array_in)
        return self.map_three_channels_ws(output_array_in)

    def map_three_channels_ws(self, output_array_in):
        r = output_array_in[0]
        g = output_array_in[1]
        b = output_array_in[2]

        output_array_out = np.zeros((3, len(r)))

        if self._led_strip == "ws2811_strip_bgr":
            output_array_out[0] = b
            output_array_out[1] = g
            output_array_out[2] = r
            return output_array_out
        if self._led_strip == "ws2811_strip_brg":
            output_array_out[0] = b
            output_array_out[1] = r
            output_array_out[2] = g
            return output_array_out
        if self._led_strip == "ws2811_strip_gbr":
            output_array_out[0] = g
            output_array_out[1] = b
            output_array_out[2] = r
            return output_array_out
        if self._led_strip == "ws2811_strip_grb":
            output_array_out[0] = g
            output_array_out[1] = r
            output_array_out[2] = b
            return output_array_out
        if self._led_strip == "ws2811_strip_rbg":
            output_array_out[0] = r
            output_array_out[1] = b
            output_array_out[2] = g
            return output_array_out

        return output_array_in

    def map_three_channels_sk(self, output_array_in):
        r = output_array_in[0]
        g = output_array_in[1]
        b = output_array_in[2]

        output_array_out = np.zeros((3, len(r)))

        if self._led_strip == "sk6812_strip_bgrw":
            output_array_out[0] = b
            output_array_out[1] = g
            output_array_out[2] = r
            return output_array_out
        if self._led_strip == "sk6812_strip_brgw":
            output_array_out[0] = b
            output_array_out[1] = r
            output_array_out[2] = g
            return output_array_out
        if self._led_strip == "sk6812_strip_gbrw":
            output_array_out[0] = g
            output_array_out[1] = b
            output_array_out[2] = r
            return output_array_out
        if self._led_strip == "sk6812_strip_grbw":
            output_array_out[0] = g
            output_array_out[1] = r
            output_array_out[2] = b
            return output_array_out
        if self._led_strip == "sk6812_strip_rbgw":
            output_array_out[0] = r
            output_array_out[1] = b
            output_array_out[2] = g
            return output_array_out

        return output_array_in

    def map_four_channels_sk(self, output_array_in):
        r = output_array_in[0]
        g = output_array_in[1]
        b = output_array_in[2]
        w = output_array_in[3]

        output_array_out = np.zeros((4, len(r)))

        if self._led_strip == "sk6812_strip_bgrw":
            output_array_out[0] = b
            output_array_out[1] = g
            output_array_out[2] = r
            output_array_out[3] = w
            return output_array_out
        if self._led_strip == "sk6812_strip_brgw":
            output_array_out[0] = b
            output_array_out[1] = r
            output_array_out[2] = g
            output_array_out[3] = w
            return output_array_out
        if self._led_strip == "sk6812_strip_gbrw":
            output_array_out[0] = g
            output_array_out[1] = b
            output_array_out[2] = r
            output_array_out[3] = w
            return output_array_out
        if self._led_strip == "sk6812_strip_grbw":
            output_array_out[0] = g
            output_array_out[1] = r
            output_array_out[2] = b
            output_array_out[3] = w
            return output_array_out
        if self._led_strip == "sk6812_strip_rbgw":
            output_array_out[0] = r
            output_array_out[1] = b
            output_array_out[2] = g
            output_array_out[3] = w
            return output_array_out

        return output_array_in
