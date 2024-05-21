from __future__ import annotations

from jsonschema import Draft202012Validator, validate  # noqa: F401
from libs.webserver.schemas.custom_types import valid_device_id, valid_group_id, valid_name_type
from loguru import logger

# Enums
effect_enum = [
    "effect_advanced_scroll",
    "effect_bars",
    "effect_beat",
    "effect_beat_slide",
    "effect_beat_twinkle",
    "effect_border",
    "effect_bubble",
    "effect_direction_changer",
    "effect_energy",
    "effect_fade",
    "effect_fireplace",
    "effect_gradient",
    "effect_pendulum",
    "effect_power",
    "effect_rods",
    "effect_scroll",
    "effect_segment_color",
    "effect_single",
    "effect_slide",
    "effect_spectrum_analyzer",
    "effect_strobe",
    "effect_sync_fade",
    "effect_twinkle",
    "effect_vu_meter",
    "effect_wave",
    "effect_wavelength",
    "effect_wiggle"
]

color_enum = [
    "black",
    "blue",
    "cyan",
    "green",
    "orange",
    "pink",
    "purple",
    "red",
    "white",
    "yellow"
]

gradient_enum = [
    "dancefloor",
    "fruity",
    "jamaica",
    "jungle",
    "jupiter",
    "ocean",
    "peach",
    "pulse",
    "rust",
    "safari",
    "spectral",
    "sunny",
    "sunset"
]

led_strips_enum = [
    "sk6812_shift_wmask",
    "sk6812_strip",
    "sk6812_strip_bgrw",
    "sk6812_strip_brgw",
    "sk6812_strip_gbrw",
    "sk6812_strip_grbw",
    "sk6812_strip_rbgw",
    "sk6812_strip_rgbw",
    "sk6812w_strip",
    "ws2811_strip_bgr",
    "ws2811_strip_brg",
    "ws2811_strip_gbr",
    "ws2811_strip_grb",
    "ws2811_strip_rbg",
    "ws2811_strip_rgb",
    "ws2812_strip"
]

log_level_enum = [
    "notset",
    "debug",
    "info",
    "warning",
    "error",
    "critical"
]

# Schemas
effect_schema = {
    "type": "object",
    "additionalProperties": False,
    "maxProperties": 29,
    "minProperties": 28,
    "required": [*effect_enum, "last_effect"],
    "properties": {
        "effect_advanced_scroll": {
            "type": "object",
            "additionalProperties": False,
            "maxProperties": 24,
            "minProperties": 24,
            "required": [
                "bass_color",
                "bass_multiplier",
                "bass_speed",
                "blur",
                "brilliance_color",
                "brilliance_multiplier",
                "brilliance_speed",
                "decay",
                "lowmid_color",
                "lowmid_multiplier",
                "lowmid_speed",
                "mid_color",
                "mid_multiplier",
                "mid_speed",
                "mirror",
                "presence_color",
                "presence_multiplier",
                "presence_speed",
                "subbass_color",
                "subbass_multiplier",
                "subbass_speed",
                "uppermid_color",
                "uppermid_multiplier",
                "uppermid_speed"
            ],
            "properties": {
                "bass_color": {
                    "enum": color_enum
                },
                "bass_multiplier": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 10
                },
                "bass_speed": {
                    "type": "integer",
                    "minimum": 0,
                    "maximum": 20
                },
                "blur": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 25
                },
                "brilliance_color": {
                    "enum": color_enum
                },
                "brilliance_multiplier": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 10
                },
                "brilliance_speed": {
                    "type": "integer",
                    "minimum": 0,
                    "maximum": 20
                },
                "decay": {
                    "type": "integer",
                    "minimum": 0,
                    "maximum": 100
                },
                "lowmid_color": {
                    "enum": color_enum
                },
                "lowmid_multiplier": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 10
                },
                "lowmid_speed": {
                    "type": "integer",
                    "minimum": 0,
                    "maximum": 20
                },
                "mid_color": {
                    "enum": color_enum
                },
                "mid_multiplier": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 10
                },
                "mid_speed": {
                    "type": "integer",
                    "minimum": 0,
                    "maximum": 20
                },
                "mirror": {"type": "boolean"},
                "presence_color": {
                    "enum": color_enum
                },
                "presence_multiplier": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 10
                },
                "presence_speed": {
                    "type": "integer",
                    "minimum": 0,
                    "maximum": 20
                },
                "subbass_color": {
                    "enum": color_enum
                },
                "subbass_multiplier": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 10
                },
                "subbass_speed": {
                    "type": "integer",
                    "minimum": 0,
                    "maximum": 20
                },
                "uppermid_color": {
                    "enum": color_enum
                },
                "uppermid_multiplier": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 10
                },
                "uppermid_speed": {
                    "type": "integer",
                    "minimum": 0,
                    "maximum": 20
                }
            }
        },
        "effect_bars": {
            "type": "object",
            "additionalProperties": False,
            "maxProperties": 6,
            "minProperties": 6,
            "required": [
                "color_mode",
                "flip_lr",
                "mirror",
                "resolution",
                "reverse_roll",
                "roll_speed"
            ],
            "properties": {
                "color_mode": {
                    "enum": gradient_enum
                },
                "flip_lr": {"type": "boolean"},
                "mirror": {"type": "boolean"},
                "resolution": {
                    "type": "integer",
                    "minimum": 0,
                    "maximum": 25
                },
                "reverse_roll": {"type": "boolean"},
                "roll_speed": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 10
                }
            }
        },
        "effect_beat": {
            "type": "object",
            "additionalProperties": False,
            "maxProperties": 5,
            "minProperties": 5,
            "required": [
                "color",
                "colorful_mode",
                "decay",
                "gradient",
                "random_color"
            ],
            "properties": {
                "color": {
                    "enum": color_enum
                },
                "colorful_mode": {"type": "boolean"},
                "decay": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 0.9
                },
                "gradient": {
                    "enum": gradient_enum
                },
                "random_color": {"type": "boolean"}
            }
        },
        "effect_beat_slide": {
            "type": "object",
            "additionalProperties": False,
            "maxProperties": 5,
            "minProperties": 5,
            "required": [
                "bar_length",
                "color",
                "decay",
                "slider_length",
                "speed"
            ],
            "properties": {
                "bar_length": {
                    "type": "integer",
                    "minimum": 0,
                    "maximum": 600
                },
                "color": {
                    "enum": color_enum
                },
                "decay": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 0.9
                },
                "slider_length": {
                    "type": "integer",
                    "minimum": 0,
                    "maximum": 200
                },
                "speed": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 20
                }
            }
        },
        "effect_beat_twinkle": {
            "type": "object",
            "additionalProperties": False,
            "maxProperties": 6,
            "minProperties": 6,
            "required": [
                "color",
                "colorful_mode",
                "decay",
                "gradient",
                "random_color",
                "star_length"
            ],
            "properties": {
                "color": {
                    "enum": color_enum
                },
                "colorful_mode": {"type": "boolean"},
                "decay": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 1
                },
                "gradient": {
                    "enum": gradient_enum
                },
                "random_color": {"type": "boolean"},
                "star_length": {
                    "type": "integer",
                    "minimum": 0,
                    "maximum": 200
                }
            }
        },
        "effect_border": {
            "type": "object",
            "additionalProperties": False,
            "maxProperties": 16,
            "minProperties": 16,
            "required": [
                "bar_count",
                "color",
                "gradient",
                "manually_resize_bars",
                "mirror",
                "reverse_roll",
                "roll_speed",
                "segment_01_end",
                "segment_01_start",
                "segment_02_end",
                "segment_02_start",
                "segment_03_end",
                "segment_03_start",
                "segment_04_end",
                "segment_04_start",
                "use_gradient"
            ],
            "properties": {
                "bar_count": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 24
                },
                "color": {
                    "enum": color_enum
                },
                "gradient": {
                    "enum": gradient_enum
                },
                "manually_resize_bars": {"type": "boolean"},
                "mirror": {"type": "boolean"},
                "reverse_roll": {"type": "boolean"},
                "roll_speed": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 10
                },
                "segment_01_start": {
                    "type": "integer",
                    "minimum": 0
                },
                "segment_01_end": {
                    "type": "integer",
                    "minimum": 0
                },
                "segment_02_start": {
                    "type": "integer",
                    "minimum": 0
                },
                "segment_02_end": {
                    "type": "integer",
                    "minimum": 0
                },
                "segment_03_start": {
                    "type": "integer",
                    "minimum": 0
                },
                "segment_03_end": {
                    "type": "integer",
                    "minimum": 0
                },
                "segment_04_start": {
                    "type": "integer",
                    "minimum": 0
                },
                "segment_04_end": {
                    "type": "integer",
                    "minimum": 0
                },
                "use_gradient": {"type": "boolean"},
            }
        },
        "effect_bubble": {
            "type": "object",
            "additionalProperties": False,
            "maxProperties": 7,
            "minProperties": 7,
            "required": [
                "blur",
                "bubble_length",
                "bubble_repeat",
                "gradient",
                "mirror",
                "reverse",
                "speed"
            ],
            "properties": {
                "blur": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 25
                },
                "bubble_length": {
                    "type": "integer",
                    "minimum": 0,
                    "maximum": 200
                },
                "bubble_repeat": {
                    "type": "integer",
                    "minimum": 0,
                    "maximum": 50
                },
                "gradient": {
                    "enum": gradient_enum
                },
                "mirror": {"type": "boolean"},
                "reverse": {"type": "boolean"},
                "speed": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 10
                }
            }
        },
        "effect_direction_changer": {
            "type": "object",
            "additionalProperties": False,
            "maxProperties": 7,
            "minProperties": 7,
            "required": [
                "bar_length",
                "bar_speed",
                "bars_in_same_direction",
                "color",
                "colorful_mode",
                "gradient",
                "random_color"
            ],
            "properties": {
                "bar_length": {
                    "type": "integer",
                    "minimum": 0,
                    "maximum": 20
                },
                "bar_speed": {
                    "type": "integer",
                    "minimum": 0,
                    "maximum": 20
                },
                "bars_in_same_direction": {
                    "type": "integer",
                    "minimum": 0,
                    "maximum": 20
                },
                "color": {
                    "enum": color_enum
                },
                "colorful_mode": {"type": "boolean"},
                "gradient": {
                    "enum": gradient_enum
                },
                "random_color": {"type": "boolean"}
            }
        },
        "effect_energy": {
            "type": "object",
            "additionalProperties": False,
            "maxProperties": 6,
            "minProperties": 6,
            "required": [
                "b_multiplier",
                "blur",
                "g_multiplier",
                "mirror",
                "r_multiplier",
                "scale"
            ],
            "properties": {
                "b_multiplier": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 50
                },
                "blur": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 200
                },
                "g_multiplier": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 50
                },
                "mirror": {"type": "boolean"},
                "r_multiplier": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 50
                },
                "scale": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 3
                }
            }
        },
        "effect_fade": {
            "type": "object",
            "additionalProperties": False,
            "maxProperties": 3,
            "minProperties": 3,
            "required": [
                "gradient",
                "reverse",
                "speed"
            ],
            "properties": {
                "gradient": {
                    "enum": gradient_enum
                },
                "reverse": {"type": "boolean"},
                "speed": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 200
                }
            }
        },
        "effect_fireplace": {
            "type": "object",
            "additionalProperties": False,
            "maxProperties": 19,
            "minProperties": 19,
            "required": [
                "blur",
                "color_variation",
                "firebase_area_maxlength",
                "firebase_area_minlength",
                "firebase_flicker_speed",
                "firebase_maincolor",
                "mask_blur",
                "mirror",
                "sparks_area_maxlength",
                "sparks_area_minlength",
                "sparks_flicker_speed",
                "sparks_fly_speed",
                "sparks_maincolor",
                "sparks_max_length",
                "sparks_maxappear_distance",
                "sparks_min_length",
                "sparks_minappear_distance",
                "swap_side",
                "use_color_variation"
            ],
            "properties": {
                "blur": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 10
                },
                "color_variation": {
                    "type": "integer",
                    "minimum": 0,
                    "maximum": 100
                },
                "firebase_area_maxlength": {
                    "type": "integer",
                    "minimum": 0,
                    "maximum": 1000
                },
                "firebase_area_minlength": {
                    "type": "integer",
                    "minimum": 0,
                    "maximum": 1000
                },
                "firebase_flicker_speed": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 10
                },
                "firebase_maincolor": {
                    "enum": color_enum
                },
                "mask_blur": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 10
                },
                "mirror": {"type": "boolean"},
                "sparks_area_maxlength": {
                    "type": "integer",
                    "minimum": 0,
                    "maximum": 1000
                },
                "sparks_area_minlength": {
                    "type": "integer",
                    "minimum": 0,
                    "maximum": 1000
                },
                "sparks_flicker_speed": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 10
                },
                "sparks_fly_speed": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 10
                },
                "sparks_maincolor": {
                    "enum": color_enum
                },
                "sparks_max_length": {
                    "type": "integer",
                    "minimum": 0,
                    "maximum": 20
                },
                "sparks_maxappear_distance": {
                    "type": "integer",
                    "minimum": 0,
                    "maximum": 1000
                },
                "sparks_min_length": {
                    "type": "integer",
                    "minimum": 0,
                    "maximum": 20
                },
                "sparks_minappear_distance": {
                    "type": "integer",
                    "minimum": 0,
                    "maximum": 1000
                },
                "swap_side": {"type": "boolean"},
                "use_color_variation": {"type": "boolean"}
            }
        },
        "effect_gradient": {
            "type": "object",
            "additionalProperties": False,
            "maxProperties": 4,
            "minProperties": 4,
            "required": [
                "gradient",
                "mirror",
                "reverse",
                "speed"
            ],
            "properties": {
                "gradient": {
                    "enum": gradient_enum
                },
                "mirror": {"type": "boolean"},
                "reverse": {"type": "boolean"},
                "speed": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 10
                }
            }
        },
        "effect_pendulum": {
            "type": "object",
            "additionalProperties": False,
            "maxProperties": 5,
            "minProperties": 5,
            "required": [
                "change_color",
                "color",
                "gradient",
                "pendulum_length",
                "speed"
            ],
            "properties": {
                "change_color": {"type": "boolean"},
                "color": {
                    "enum": color_enum
                },
                "gradient": {
                    "enum": gradient_enum
                },
                "pendulum_length": {
                    "type": "integer",
                    "minimum": 0,
                    "maximum": 200
                },
                "speed": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 20
                }
            }
        },
        "effect_power": {
            "type": "object",
            "additionalProperties": False,
            "maxProperties": 5,
            "minProperties": 5,
            "required": [
                "color_mode",
                "flip_lr",
                "mirror",
                "s_color",
                "s_count"
            ],
            "properties": {
                "color_mode": {
                    "enum": gradient_enum
                },
                "flip_lr": {"type": "boolean"},
                "mirror": {"type": "boolean"},
                "s_color": {
                    "enum": color_enum
                },
                "s_count": {
                    "type": "integer",
                    "minimum": 0,
                    "maximum": 200
                }
            }
        },
        "effect_random_cycle": {
            "type": "object",
            "additionalProperties": False,
            "maxProperties": 28,
            "minProperties": 28,
            "required": [*effect_enum, "interval"],
            "properties": {
                "effect_advanced_scroll": {"type": "boolean"},
                "effect_bars": {"type": "boolean"},
                "effect_beat": {"type": "boolean"},
                "effect_beat_slide": {"type": "boolean"},
                "effect_beat_twinkle": {"type": "boolean"},
                "effect_border": {"type": "boolean"},
                "effect_bubble": {"type": "boolean"},
                "effect_direction_changer": {"type": "boolean"},
                "effect_energy": {"type": "boolean"},
                "effect_fade": {"type": "boolean"},
                "effect_fireplace": {"type": "boolean"},
                "effect_gradient": {"type": "boolean"},
                "effect_pendulum": {"type": "boolean"},
                "effect_power": {"type": "boolean"},
                "effect_rods": {"type": "boolean"},
                "effect_scroll": {"type": "boolean"},
                "effect_segment_color": {"type": "boolean"},
                "effect_single": {"type": "boolean"},
                "effect_slide": {"type": "boolean"},
                "effect_spectrum_analyzer": {"type": "boolean"},
                "effect_strobe": {"type": "boolean"},
                "effect_sync_fade": {"type": "boolean"},
                "effect_twinkle": {"type": "boolean"},
                "effect_vu_meter": {"type": "boolean"},
                "effect_wave": {"type": "boolean"},
                "effect_wavelength": {"type": "boolean"},
                "effect_wiggle": {"type": "boolean"},
                "interval": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 3600
                },
            }
        },
        "effect_rods": {
            "type": "object",
            "additionalProperties": False,
            "maxProperties": 8,
            "minProperties": 8,
            "required": [
                "change_color",
                "color",
                "gradient",
                "mirror",
                "reverse",
                "rods_distance",
                "rods_length",
                "speed"
            ],
            "properties": {
                "change_color": {"type": "boolean"},
                "color": {
                    "enum": color_enum
                },
                "gradient": {
                    "enum": gradient_enum
                },
                "mirror": {"type": "boolean"},
                "reverse": {"type": "boolean"},
                "rods_distance": {
                    "type": "integer",
                    "minimum": 0,
                    "maximum": 200
                },
                "rods_length": {
                    "type": "integer",
                    "minimum": 0,
                    "maximum": 200
                },
                "speed": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 10
                }
            }
        },
        "effect_scroll": {
            "type": "object",
            "additionalProperties": False,
            "maxProperties": 12,
            "minProperties": 12,
            "required": [
                "blur",
                "decay",
                "high_color",
                "high_multiplier",
                "high_speed",
                "low_speed",
                "lows_color",
                "lows_multiplier",
                "mid_speed",
                "mids_color",
                "mids_multiplier",
                "mirror"
            ],
            "properties": {
                "blur": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 25
                },
                "decay": {
                    "type": "integer",
                    "minimum": 0,
                    "maximum": 100
                },
                "high_color": {
                    "enum": color_enum
                },
                "high_multiplier": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 10
                },
                "high_speed": {
                    "type": "integer",
                    "minimum": 0,
                    "maximum": 20
                },
                "low_speed": {
                    "type": "integer",
                    "minimum": 0,
                    "maximum": 20
                },
                "lows_color": {
                    "enum": color_enum
                },
                "lows_multiplier": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 10
                },
                "mid_speed": {
                    "type": "integer",
                    "minimum": 0,
                    "maximum": 20
                },
                "mids_color": {
                    "enum": color_enum
                },
                "mids_multiplier": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 10
                },
                "mirror": {"type": "boolean"}
            }
        },
        "effect_segment_color": {
            "type": "object",
            "additionalProperties": False,
            "maxProperties": 30,
            "minProperties": 30,
            "required": [
                "segment_01_color",
                "segment_01_end",
                "segment_01_start",
                "segment_02_color",
                "segment_02_end",
                "segment_02_start",
                "segment_03_color",
                "segment_03_end",
                "segment_03_start",
                "segment_04_color",
                "segment_04_end",
                "segment_04_start",
                "segment_05_color",
                "segment_05_end",
                "segment_05_start",
                "segment_06_color",
                "segment_06_end",
                "segment_06_start",
                "segment_07_color",
                "segment_07_end",
                "segment_07_start",
                "segment_08_color",
                "segment_08_end",
                "segment_08_start",
                "segment_09_color",
                "segment_09_end",
                "segment_09_start",
                "segment_10_color",
                "segment_10_end",
                "segment_10_start"
            ],
            "properties": {
                "segment_01_color": {
                    "enum": color_enum
                },
                "segment_01_end": {
                    "type": "integer",
                    "minimum": 0
                },
                "segment_01_start": {
                    "type": "integer",
                    "minimum": 0
                },
                "segment_02_color": {
                    "enum": color_enum
                },
                "segment_02_end": {
                    "type": "integer",
                    "minimum": 0
                },
                "segment_02_start": {
                    "type": "integer",
                    "minimum": 0
                },
                "segment_03_color": {
                    "enum": color_enum
                },
                "segment_03_end": {
                    "type": "integer",
                    "minimum": 0
                },
                "segment_03_start": {
                    "type": "integer",
                    "minimum": 0
                },
                "segment_04_color": {
                    "enum": color_enum
                },
                "segment_04_end": {
                    "type": "integer",
                    "minimum": 0
                },
                "segment_04_start": {
                    "type": "integer",
                    "minimum": 0
                },
                "segment_05_color": {
                    "enum": color_enum
                },
                "segment_05_end": {
                    "type": "integer",
                    "minimum": 0
                },
                "segment_05_start": {
                    "type": "integer",
                    "minimum": 0
                },
                "segment_06_color": {
                    "enum": color_enum
                },
                "segment_06_end": {
                    "type": "integer",
                    "minimum": 0
                },
                "segment_06_start": {
                    "type": "integer",
                    "minimum": 0
                },
                "segment_07_color": {
                    "enum": color_enum
                },
                "segment_07_end": {
                    "type": "integer",
                    "minimum": 0
                },
                "segment_07_start": {
                    "type": "integer",
                    "minimum": 0
                },
                "segment_08_color": {
                    "enum": color_enum
                },
                "segment_08_end": {
                    "type": "integer",
                    "minimum": 0
                },
                "segment_08_start": {
                    "type": "integer",
                    "minimum": 0
                },
                "segment_09_color": {
                    "enum": color_enum
                },
                "segment_09_end": {
                    "type": "integer",
                    "minimum": 0
                },
                "segment_09_start": {
                    "type": "integer",
                    "minimum": 0
                },
                "segment_10_color": {
                    "enum": color_enum
                },
                "segment_10_end": {
                    "type": "integer",
                    "minimum": 0
                },
                "segment_10_start": {
                    "type": "integer",
                    "minimum": 0
                }
            }
        },
        "effect_single": {
            "type": "object",
            "additionalProperties": False,
            "maxProperties": 4,
            "minProperties": 4,
            "required": [
                "color",
                "custom_color",
                "use_custom_color",
                "white"
            ],
            "properties": {
                "color": {
                    "enum": color_enum
                },
                "custom_color": {"$ref": "#/$defs/rgb"},
                "use_custom_color": {"type": "boolean"},
                "white": {
                    "type": "integer",
                    "minimum": 0,
                    "maximum": 255
                },
            }
        },
        "effect_slide": {
            "type": "object",
            "additionalProperties": False,
            "maxProperties": 4,
            "minProperties": 4,
            "required": [
                "gradient",
                "mirror",
                "reverse",
                "speed"
            ],
            "properties": {
                "gradient": {
                    "enum": gradient_enum
                },
                "mirror": {"type": "boolean"},
                "reverse": {"type": "boolean"},
                "speed": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 10
                }
            }
        },
        "effect_spectrum_analyzer": {
            "type": "object",
            "additionalProperties": False,
            "maxProperties": 2,
            "minProperties": 2,
            "required": [
                "color",
                "spectrum_count"
            ],
            "properties": {
                "color": {
                    "enum": color_enum
                },
                "spectrum_count": {
                    "type": "integer",
                    "minimum": 0,
                    "maximum": 24
                }
            }
        },
        "effect_strobe": {
            "type": "object",
            "additionalProperties": False,
            "maxProperties": 5,
            "minProperties": 5,
            "required": [
                "color",
                "custom_color",
                "speed",
                "use_custom_color",
                "white"
            ],
            "properties": {
                "color": {
                    "enum": color_enum
                },
                "custom_color": {"$ref": "#/$defs/rgb"},
                "speed": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 100
                },
                "use_custom_color": {"type": "boolean"},
                "white": {
                    "type": "integer",
                    "minimum": 0,
                    "maximum": 255
                },
            }
        },
        "effect_sync_fade": {
            "type": "object",
            "additionalProperties": False,
            "maxProperties": 3,
            "minProperties": 3,
            "required": [
                "gradient",
                "reverse",
                "speed"
            ],
            "properties": {
                "gradient": {
                    "enum": gradient_enum
                },
                "reverse": {"type": "boolean"},
                "speed": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 200
                }
            }
        },
        "effect_twinkle": {
            "type": "object",
            "additionalProperties": False,
            "maxProperties": 7,
            "minProperties": 7,
            "required": [
                "blur",
                "gradient",
                "star_ascending_speed",
                "star_descending_speed",
                "star_rising_speed",
                "stars_count",
                "stars_length"
            ],
            "properties": {
                "blur": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 200
                },
                "gradient": {
                    "enum": gradient_enum
                },
                "star_ascending_speed": {
                    "type": "integer",
                    "minimum": 0,
                    "maximum": 200
                },
                "star_descending_speed": {
                    "type": "integer",
                    "minimum": 0,
                    "maximum": 200
                },
                "star_rising_speed": {
                    "type": "integer",
                    "minimum": 0,
                    "maximum": 200
                },
                "stars_count": {
                    "type": "integer",
                    "minimum": 0,
                    "maximum": 200
                },
                "stars_length": {
                    "type": "integer",
                    "minimum": 0,
                    "maximum": 200
                }
            }
        },
        "effect_vu_meter": {
            "type": "object",
            "additionalProperties": False,
            "maxProperties": 6,
            "minProperties": 6,
            "required": [
                "bar_length",
                "color",
                "gradient",
                "max_vol_color",
                "speed",
                "use_gradient"
            ],
            "properties": {
                "bar_length": {
                    "type": "integer",
                    "minimum": 0,
                    "maximum": 200
                },
                "color": {
                    "enum": color_enum
                },
                "gradient": {
                    "enum": gradient_enum
                },
                "max_vol_color": {
                    "enum": color_enum
                },
                "speed": {
                    "type": "integer",
                    "minimum": 0,
                    "maximum": 100
                },
                "use_gradient": {"type": "boolean"}
            }
        },
        "effect_wave": {
            "type": "object",
            "additionalProperties": False,
            "maxProperties": 5,
            "minProperties": 5,
            "required": [
                "color_flash",
                "color_wave",
                "decay",
                "wipe_len",
                "wipe_speed"
            ],
            "properties": {
                "color_flash": {
                    "enum": color_enum
                },
                "color_wave": {
                    "enum": color_enum
                },
                "decay": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 5
                },
                "wipe_len": {
                    "type": "integer",
                    "minimum": 0,
                    "maximum": 200
                },
                "wipe_speed": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 25
                }
            }
        },
        "effect_wavelength": {
            "type": "object",
            "additionalProperties": False,
            "maxProperties": 7,
            "minProperties": 7,
            "required": [
                "blur",
                "color_mode",
                "flip_lr",
                "mirror",
                "reverse_grad",
                "reverse_roll",
                "roll_speed"
            ],
            "properties": {
                "blur": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 200
                },
                "color_mode": {
                    "enum": gradient_enum
                },
                "flip_lr": {"type": "boolean"},
                "mirror": {"type": "boolean"},
                "reverse_grad": {"type": "boolean"},
                "reverse_roll": {"type": "boolean"},
                "roll_speed": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 10
                }
            }
        },
        "effect_wiggle": {
            "type": "object",
            "additionalProperties": False,
            "maxProperties": 4,
            "minProperties": 4,
            "required": [
                "bar_length",
                "beat_color",
                "color",
                "decay"
            ],
            "properties": {
                "bar_length": {
                    "type": "integer",
                    "minimum": 0,
                    "maximum": 200
                },
                "beat_color": {
                    "enum": color_enum
                },
                "color": {
                    "enum": color_enum
                },
                "decay": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 0.9
                }
            }
        },
        "last_effect": {
            "enum": [*effect_enum, "effect_off"]
        }
    }
}

device_schema = {
    "type": "object",
    "additionalProperties": False,
    "maxProperties": 10,
    "minProperties": 10,
    "required": [
        "device_groups",
        "device_name",
        "effects",
        "fps",
        "led_brightness",
        "led_count",
        "led_mid",
        "led_strip",
        "output",
        "output_type"
    ],
    "properties": {
        "device_groups": {
            "type": "object",
            "additionalProperties": False,
            "maxProperties": 100,
            "minProperties": 0,
            "patternProperties": {
                valid_group_id: valid_name_type
            },
        },
        "device_name": {
            "anyOf": [
                valid_name_type,
                {
                    "const": "Default Device"
                }
            ],
        },
        "effects": effect_schema,
        "fps": {
            "type": "integer",
            "minimum": 1,
            "maximum": 1000
        },
        "led_brightness": {
            "type": "integer",
            "minimum": 0,
            "maximum": 100
        },
        "led_count": {
            "type": "integer",
            "minimum": 7
        },
        "led_mid": {
            "type": "integer",
            "minimum": 1
        },
        "led_strip": {
            "enum": led_strips_enum
        },
        "output": {
            "type": "object",
            "additionalProperties": False,
            "maxProperties": 3,
            "minProperties": 3,
            "required": [
                "output_mqtt",
                "output_raspi",
                "output_udp"
            ],
            "properties": {
                "output_mqtt": {
                    "type": "object",
                    "additionalProperties": False,
                    "maxProperties": 2,
                    "minProperties": 2,
                    "required": [
                        "mqtt_broker",
                        "mqtt_path"
                    ],
                    "properties": {
                        "mqtt_broker": {
                            "type": "string",
                            "minLength": 1
                        },
                        "mqtt_path": {
                            "type": "string",
                            "minLength": 1
                        }
                    }
                },
                "output_raspi": {
                    "type": "object",
                    "additionalProperties": False,
                    "maxProperties": 5,
                    "minProperties": 5,
                    "required": [
                        "led_channel",
                        "led_dma",
                        "led_freq_hz",
                        "led_invert",
                        "led_pin"
                    ],
                    "properties": {
                        "led_channel": {
                            "enum": [
                                0,
                                1
                            ]
                        },
                        "led_dma": {
                            "type": "integer",
                            "minimum": 0,
                            "maximum": 14
                        },
                        "led_freq_hz": {
                            "type": "integer",
                            "minimum": 0,
                            "maximum": 1000000
                        },
                        "led_invert": {"type": "boolean"},
                        "led_pin": {
                            "enum": [
                                13,
                                18
                            ]
                        }
                    }
                },
                "output_udp": {
                    "type": "object",
                    "additionalProperties": False,
                    "maxProperties": 2,
                    "minProperties": 2,
                    "required": [
                        "udp_client_ip",
                        "udp_client_port"
                    ],
                    "properties": {
                        "udp_client_ip": {
                            "type": "string",
                            "format": "ipv4"
                        },
                        "udp_client_port": {
                            "oneOf": [
                                {
                                    "type": "integer",
                                    "minimum": 0,
                                    "maximum": 65535
                                },
                                {"type": "string"}
                            ]
                        }
                    }
                },
            }
        },
        "output_type": {
            "enum": [
                "output_raspi",
                "output_udp",
                "output_mqtt"
            ]
        }
    }
}

colors_schema = {
    "type": "object",
    "additionalProperties": False,
    "maxProperties": 10,
    "minProperties": 10,
    "required": color_enum,
    "properties": {
        "black": {"$ref": "#/$defs/rgb"},
        "blue": {"$ref": "#/$defs/rgb"},
        "cyan": {"$ref": "#/$defs/rgb"},
        "green": {"$ref": "#/$defs/rgb"},
        "orange": {"$ref": "#/$defs/rgb"},
        "pink": {"$ref": "#/$defs/rgb"},
        "purple": {"$ref": "#/$defs/rgb"},
        "red": {"$ref": "#/$defs/rgb"},
        "white": {"$ref": "#/$defs/rgb"},
        "yellow": {"$ref": "#/$defs/rgb"}
    }
}

development_config_schema = {
    "type": "object",
    "additionalProperties": False,
    "maxProperties": 2,
    "minProperties": 2,
    "required": [
        "deactivate_output",
        "test"
    ],
    "properties": {
        "deactivate_output": {"type": "boolean"},
        "test": {
            "const": "first"
        }
    }
}

device_configs_schema = {
    "type": "object",
    "additionalProperties": False,
    "maxProperties": 100,
    "minProperties": 0,
    "patternProperties": {
        valid_device_id: device_schema
    }
}

general_settings_schema = {
    "type": "object",
    "additionalProperties": False,
    "maxProperties": 13,
    "minProperties": 13,
    "required": [
        "default_sample_rate",
        "device_groups",
        "device_id",
        "frames_per_buffer",
        "log_file_enabled",
        "log_level_console",
        "log_level_file",
        "max_frequency",
        "min_frequency",
        "min_volume_threshold",
        "n_fft_bins",
        "n_rolling_history",
        "webserver_port"
    ],
    "properties": {
        "default_sample_rate": {
            "enum": [
                44100,
                48000
            ]
        },
        "device_groups": {
            "type": "object",
            "additionalProperties": False,
            "maxProperties": 100,
            "minProperties": 0,
            "patternProperties": {
                valid_group_id: valid_name_type
            }
        },
        "device_id": {
            "type": "integer",
            "minimum": -1,
            "maximum": 100
        },
        "frames_per_buffer": {
            "type": "integer",
            "multipleOf": 2
        },
        "log_file_enabled": {"type": "boolean"},
        "log_level_console": {
            "enum": log_level_enum
        },
        "log_level_file": {
            "enum": log_level_enum
        },
        "max_frequency": {
            "type": "integer",
            "minimum": 0,
            "maximum": 140000
        },
        "min_frequency": {
            "type": "integer",
            "minimum": 0,
            "maximum": 140000
        },
        "min_volume_threshold": {
            "type": "number",
            "minimum": 0,
            "maximum": 1
        },
        "n_fft_bins": {
            "type": "integer",
            "multipleOf": 2
        },
        "n_rolling_history": {
            "type": "integer",
            "multipleOf": 2
        },
        "webserver_port": {
            "type": "integer",
            "minimum": 0,
            "maximum": 65535
        },
    }
}

gradients_schema = {
    "type": "object",
    "additionalProperties": False,
    "maxProperties": 13,
    "minProperties": 13,
    "required": gradient_enum,
    "properties": {
        "dancefloor": {
            "type": "array",
            "items": {"$ref": "#/$defs/rgb"},
            "maxItems": 4,
            "minItems": 4
        },
        "fruity": {
            "type": "array",
            "items": {"$ref": "#/$defs/rgb"},
            "maxItems": 2,
            "minItems": 2
        },
        "jamaica": {
            "type": "array",
            "items": {"$ref": "#/$defs/rgb"},
            "maxItems": 2,
            "minItems": 2
        },
        "jungle": {
            "type": "array",
            "items": {"$ref": "#/$defs/rgb"},
            "maxItems": 3,
            "minItems": 3
        },
        "jupiter": {
            "type": "array",
            "items": {"$ref": "#/$defs/rgb"},
            "maxItems": 2,
            "minItems": 2
        },
        "ocean": {
            "type": "array",
            "items": {"$ref": "#/$defs/rgb"},
            "maxItems": 3,
            "minItems": 3
        },
        "peach": {
            "type": "array",
            "items": {"$ref": "#/$defs/rgb"},
            "maxItems": 2,
            "minItems": 2
        },
        "pulse": {
            "type": "array",
            "items": {"$ref": "#/$defs/rgb"},
            "maxItems": 3,
            "minItems": 3
        },
        "rust": {
            "type": "array",
            "items": {"$ref": "#/$defs/rgb"},
            "maxItems": 2,
            "minItems": 2
        },
        "safari": {
            "type": "array",
            "items": {"$ref": "#/$defs/rgb"},
            "maxItems": 3,
            "minItems": 3
        },
        "spectral": {
            "type": "array",
            "items": {"$ref": "#/$defs/rgb"},
            "maxItems": 8,
            "minItems": 8
        },
        "sunny": {
            "type": "array",
            "items": {"$ref": "#/$defs/rgb"},
            "maxItems": 4,
            "minItems": 4
        },
        "sunset": {
            "type": "array",
            "items": {"$ref": "#/$defs/rgb"},
            "maxItems": 3,
            "minItems": 3
        }
    }
}

led_strips_schema = {
    "type": "object",
    "additionalProperties": False,
    "maxProperties": 16,
    "minProperties": 16,
    "required": led_strips_enum,
    "properties": {
        "sk6812_shift_wmask": {
            "const": "sk6812_shift_wmask"
        },
        "sk6812_strip": {
            "const": "sk6812_default"
        },
        "sk6812_strip_bgrw": {
            "const": "sk6812_strip_bgrw"
        },
        "sk6812_strip_brgw": {
            "const": "sk6812_strip_brgw"
        },
        "sk6812_strip_gbrw": {
            "const": "sk6812_strip_gbrw"
        },
        "sk6812_strip_grbw": {
            "const": "sk6812_strip_grbw"
        },
        "sk6812_strip_rbgw": {
            "const": "sk6812_strip_rbgw"
        },
        "sk6812_strip_rgbw": {
            "const": "sk6812_strip_rgbw"
        },
        "sk6812w_strip": {
            "const": "sk6812w_default"
        },
        "ws2811_strip_bgr": {
            "const": "ws281x_bgr"
        },
        "ws2811_strip_brg": {
            "const": "ws281x_brg"
        },
        "ws2811_strip_gbr": {
            "const": "ws281x_gbr"
        },
        "ws2811_strip_grb": {
            "const": "ws281x_grb"
        },
        "ws2811_strip_rbg": {
            "const": "ws281x_rbg"
        },
        "ws2811_strip_rgb": {
            "const": "ws281x_rgb"
        },
        "ws2812_strip": {
            "const": "ws281x_default"
        },
    }
}

logging_levels_schema = {
    "type": "object",
    "additionalProperties": False,
    "maxProperties": 6,
    "minProperties": 6,
    "required": log_level_enum,
    "properties": {
        "critical": {
            "const": "Critical"
        },
        "debug": {
            "const": "Debug"
        },
        "error": {
            "const": "Error"
        },
        "info": {
            "const": "Info"
        },
        "notset": {
            "const": "Not Set"
        },
        "warning": {
            "const": "Warning"
        },
    }
}

version_schema = {
    "type": "integer",
    "minimum": 2,
    "maximum": 3
}

definitions = {
    "rgb": {
        "type": "array",
        "items": {
            "type": "integer",
            "minimum": 0,
            "maximum": 255
        },
        "maxItems": 3,
        "minItems": 3
    }
}

# Config schema
schema = {
    "type": "object",
    "additionalProperties": False,
    "maxProperties": 9,
    "minProperties": 9,
    "required": [
        "colors",
        "default_device",
        "development_config",
        "device_configs",
        "general_settings",
        "gradients",
        "led_strips",
        "logging_levels",
        "version"
    ],
    "properties": {
        "colors": colors_schema,
        "default_device": device_schema,
        "development_config": development_config_schema,
        "device_configs": device_configs_schema,
        "general_settings": general_settings_schema,
        "gradients": gradients_schema,
        "led_strips": led_strips_schema,
        "logging_levels": logging_levels_schema,
        "version": version_schema
    },
    "$defs": definitions
}


class ConfigValidatorService:
    def __init__(self: ConfigValidatorService) -> None:
        self.schema = self._get_schema()

    @staticmethod
    def _get_schema() -> dict:
        return schema

    def validate_config(self: ConfigValidatorService, config):
        v = Draft202012Validator(self.schema, format_checker=Draft202012Validator.FORMAT_CHECKER)
        errors = sorted(v.iter_errors(config), key=lambda e: e.path)
        for e in errors:
            logger.error(f"\nError text: {e.message}.\nError path: {e.json_path}\n")

        # Validate will raise exception if given json is not
        # what is described in schema.
        # validate(instance=config, schema=self.schema)


def remove_required_keys(schema: dict | list) -> dict | list:
    """Remove `required` and `minProperties` keys from config validator schema, so that a partial update is allowed."""
    if isinstance(schema, dict):
        new_obj = {}
        for key, value in schema.items():
            if key in {"required", "minProperties"}:
                continue
            new_obj[key] = remove_required_keys(value)
        return new_obj
    if isinstance(schema, list):
        return [remove_required_keys(item) for item in schema]

    # print(type(schema), schema)
    return schema
    # raise TypeError("Schema must be dict or list.")
