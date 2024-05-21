from __future__ import annotations

from libs.audio_info import AudioInfo  # pylint: disable=E0611, E0401
from libs.effects_enum import EffectNames, EffectsEnum  # pylint: disable=E0611, E0401
from libs.webserver.executer_base import ExecuterBase


class GeneralExecuter(ExecuterBase):

    def get_colors(self) -> dict[str, str]:
        """Return colors."""
        return {key: key for key in self._config["colors"]}

    def get_gradients(self) -> dict[str, str]:
        """Return gradients."""
        return {key: key for key in self._config["gradients"]}

    def get_led_strips(self) -> dict[str, str]:
        """Return LED strips."""
        return dict(self._config["led_strips"])

    def get_logging_levels(self) -> dict[str, str]:
        """Return logging levels."""
        return dict(self._config["logging_levels"])

    def get_audio_devices(self) -> dict:
        """Return audio devices."""
        audio_devices = AudioInfo.get_audio_devices(self._py_audio)
        return {value.device_id: value.to_string() for value in audio_devices}

    @staticmethod
    def get_output_types() -> dict[str, str]:
        """Return output types."""
        return {
            "output_raspi": "Output Raspberry Pi",
            "output_udp": "Output Network via UDP"
        }

    @staticmethod
    def get_effects() -> dict[str, dict]:
        """Return effects."""
        return {
            "non_music": EffectNames.non_music,
            "music": EffectNames.music,
            "special": EffectNames.special,
            "order": {effect.name: index for index, effect in enumerate(EffectsEnum, 1)}
        }
