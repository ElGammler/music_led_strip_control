
from loguru import logger

from libs.audio_device import AudioDevice  # pylint: disable=E0611, E0401


class AudioInfo:
    def get_audio_devices(py_audio):
        logger.debug("Get audio devices.")
        audio_devices = []

        try:
            audio_device_count = py_audio.get_device_count()
            logger.debug(f"Available audio devices (input and output): {audio_device_count}")
            try:
                for i in range(audio_device_count):
                    raw_audio_device = py_audio.get_device_info_by_host_api_device_index(0, i)

                    if raw_audio_device["maxInputChannels"] >= 1:
                        audio_device = AudioInfo.parse_raw_audio_device_to_audio_device(raw_audio_device)
                        logger.debug(f"Found audio Device: {audio_device.to_string()}")
                        audio_devices.append(audio_device)

            except Exception:
                logger.exception("Unexpected error in AudioInfo.")

        except OSError as e:
            logger.error(f"OS error: {e}")
        except Exception:
            logger.exception("Unexpected error in AudioInfo.")

        logger.debug(f"Found {len(audio_devices)} audio devices.")
        return audio_devices

    def get_default_audio_device(py_audio):
        default_device = AudioDevice(0, "Error", 44100)
        try:
            raw_default_device = py_audio.get_default_input_device_info()
            default_device = AudioInfo.parse_raw_audio_device_to_audio_device(raw_default_device)

        except OSError as e:
            logger.error(f"OS error: {e}")
        except Exception:
            logger.error("Unexpected error in AudioInfo get_default_audio_device.")

        return default_device

    def parse_raw_audio_device_to_audio_device(raw_audio_device):
        device_id = raw_audio_device["index"]
        name = raw_audio_device["name"]
        default_sample_rate = raw_audio_device["defaultSampleRate"]
        return AudioDevice(device_id, name, default_sample_rate)
