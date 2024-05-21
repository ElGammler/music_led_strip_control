from enum import Enum
from typing import ClassVar


class EffectNames:
    """Add a new effect ID and Name to the correct dictionary in this class."""

    non_music: ClassVar[dict[str, str]] = {
        "effect_single": "Single",
        "effect_gradient": "Gradient",
        "effect_fade": "Fade",
        "effect_sync_fade": "Sync Fade",
        "effect_slide": "Slide",
        "effect_bubble": "Bubble",
        "effect_twinkle": "Twinkle",
        "effect_pendulum": "Pendulum",
        "effect_rods": "Rods",
        "effect_segment_color": "Segment Color",
        "effect_fireplace": "Fireplace",
        "effect_strobe": "Strobe"
    }

    music: ClassVar[dict[str, str]] = {
        "effect_scroll": "Scroll",
        "effect_advanced_scroll": "Advanced Scroll",
        "effect_energy": "Energy",
        "effect_wavelength": "Wavelength",
        "effect_bars": "Bars",
        "effect_power": "Power",
        "effect_beat": "Beat",
        "effect_beat_twinkle": "Beat Twinkle",
        "effect_beat_slide": "Beat Slide",
        "effect_wave": "Wave",
        "effect_wiggle": "Wiggle",
        "effect_vu_meter": "VU Meter",
        "effect_spectrum_analyzer": "Spectrum Analyzer",
        "effect_direction_changer": "Direction Changer",
        "effect_border": "Border"
    }

    special: ClassVar[dict[str, str]] = {
        "effect_off": "Off",
        "effect_random_cycle": "Random Cycle",
        "effect_random_non_music": "Random Non-Music",
        "effect_random_music": "Random Music"
    }


# Dynamically create `EffectsEnum`, so that only one place (`EffectNames`)
# needs to be changed when adding new effects.
EffectsEnum = Enum("EffectsEnum", {**EffectNames.non_music, **EffectNames.music, **EffectNames.special})
