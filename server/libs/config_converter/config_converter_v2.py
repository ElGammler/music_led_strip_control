import json
import os

from loguru import logger

from libs.config_converter.config_converter_base import ConfigConverterBase  # pylint: disable=E0611, E0401


class ConfigConverterV2(ConfigConverterBase):
    def __init__(self) -> None:
        self.from_version = 1
        self.to_version = 2

    def upgrade(self, old_config):
        logger.info("Upgrade config to version 2.")
        rel_config_path = "../../.mlsc/"
        config_folder = os.path.abspath(rel_config_path) + "/"
        tmp_convert_file_path = config_folder + "tmp_config_convert.json"

        # self.delete_tmp_json(tmp_convert_file_path)
        # self.save_tmp_json(old_config, tmp_convert_file_path)

        # with fileinput.FileInput(tmp_convert_file_path, inplace=True) as file:
        #     for line in file:
        #         renamed_line = self.rename_line(line)
        #         file.write(renamed_line)

        # new_config = self.read_tmp_json(tmp_convert_file_path)
        # self.delete_tmp_json(tmp_convert_file_path)

        json_string = self.dict_to_json_string(old_config)
        renamed_json_string = self.rename_config(json_string)
        new_config = self.json_string_to_dict(renamed_json_string)

        new_config["version"] = 2

        logger.info("Config upgraded to version 2.")
        return new_config

    def save_tmp_json(self, old_config, tmp_convert_file_path):
        try:
            logger.debug("Save tmp config file.")
            # Write tmp file
            with open(tmp_convert_file_path, "w") as write_file:
                json.dump(old_config, write_file, indent=4, sort_keys=True)

        except Exception as e:
            logger.exception(f"Exception while saving the tmp file: {e}")

    def delete_tmp_json(self, tmp_convert_file_path):
        try:
            logger.debug("Delete tmp config file.")
            # Search and delete tmp file
            if os.path.exists(tmp_convert_file_path):
                os.remove(tmp_convert_file_path)
        except Exception as e:
            logger.exception(f"Exception while delete the tmp file: {e}")

    def read_tmp_json(self, tmp_convert_file_path):
        try:
            logger.debug("Read tmp config file.")
            with open(tmp_convert_file_path, "r") as read_file:
                return json.load(read_file)
        except Exception as e:
            logger.exception(f"Exception while read the tmp file: {e}")

    def dict_to_json_string(self, old_config_dict):
        return json.dumps(old_config_dict)

    def json_string_to_dict(self, old_config_string):
        return json.loads(old_config_string)

    def rename_config(self, json_string):
        rename_map = self.get_rename_map()

        for key, value in rename_map.items():
            json_string = json_string.replace(key, value)

        return json_string

    def get_rename_map(self):
        # rename map describes the changes of the config. "before_value" : "after_value"
        rename_map = {
            "colours": "colors",
            "Black": "black",
            "Blue": "blue",
            "Cyan": "cyan",
            "Green": "green",
            "Orange": "orange",
            "Pink": "pink",
            "Purple": "purple",
            "Red": "red",
            "White": "white",
            "Yellow": "yellow",
            "DEVICE_NAME": "device_name",
            "FPS": "fps",
            "LED_Count": "led_count",
            "LED_Mid": "led_mid",
            "LED_Strip": "led_strip",
            "LED_Brightness": "led_brightness",
            "OUTPUT_TYPE": "output_type",
            "MQTT_Broker": "mqtt_broker",
            "MQTT_Path": "mqtt_path",
            "LED_Channel": "led_channel",
            "LED_Dma": "led_dma",
            "LED_Freq_Hz": "led_freq_hz",
            "LED_Invert": "led_invert",
            "LED_Pin": "led_pin",
            "UDP_Client_IP": "udp_client_ip",
            "UDP_Client_Port": "udp_client_port",
            "DEFAULT_SAMPLE_RATE": "default_sample_rate",
            "DEVICE_ID": "device_id",
            "FRAMES_PER_BUFFER": "frames_per_buffer",
            "LOG_FILE_ENABLED": "log_file_enabled",
            "LOG_LEVEL_CONSOLE": "log_level_console",
            "LOG_LEVEL_FILE": "log_level_file",
            "MAX_FREQUENCY": "max_frequency",
            "MIN_FREQUENCY": "min_frequency",
            "MIN_VOLUME_THRESHOLD": "min_volume_threshold",
            "N_FFT_BINS": "n_fft_bins",
            "N_ROLLING_HISTORY": "n_rolling_history",
            "WEBSERVER_PORT": "webserver_port",
            "Dancefloor": "dancefloor",
            "Fruity": "fruity",
            "Jamaica": "jamaica",
            "Jungle": "jungle",
            "Jupiter": "jupiter",
            "Ocean": "ocean",
            "Peach": "peach",
            "Rust": "rust",
            "Safari": "safari",
            "Spectral": "spectral",
            "Sunny": "sunny",
            "Sunset": "sunset",
            "SK6812W_STRIP": "sk6812w_strip",
            "SK6812_SHIFT_WMASK": "sk6812_shift_wmask",
            "SK6812_STRIP": "sk6812_strip",
            "SK6812_STRIP_BGRW": "sk6812_strip_bgrw",
            "SK6812_STRIP_BRGW": "sk6812_strip_brgw",
            "SK6812_STRIP_GBRW": "sk6812_strip_gbrw",
            "SK6812_STRIP_GRBW": "sk6812_strip_grbw",
            "SK6812_STRIP_RBGW": "sk6812_strip_rbgw",
            "SK6812_STRIP_RGBW": "sk6812_strip_rgbw",
            "WS2811_STRIP_BGR": "ws2811_strip_bgr",
            "WS2811_STRIP_BRG": "ws2811_strip_brg",
            "WS2811_STRIP_GBR": "ws2811_strip_gbr",
            "WS2811_STRIP_GRB": "ws2811_strip_grb",
            "WS2811_STRIP_RBG": "ws2811_strip_rbg",
            "WS2811_STRIP_RGB": "ws2811_strip_rgb",
            "WS2812_STRIP": "ws2812_strip",
            "SK6812W_default": "sk6812w_default",
            "SK6812_default": "sk6812_default",
            "WS281x_BGR": "ws281x_bgr",
            "WS281x_BRG": "ws281x_brg",
            "WS281x_GBR": "ws281x_gbr",
            "WS281x_GRB": "ws281x_grb",
            "WS281x_RBG": "ws281x_rbg",
            "WS281x_RGB": "ws281x_rgb",
            "WS281x_default": "ws281x_default",
            "NOTSET": "notset",
            "DEBUG": "debug",
            "INFO": "info",
            "WARNING": "warning",
            "ERROR": "error",
            "CRITICAL": "critical"
        }

        return rename_map
