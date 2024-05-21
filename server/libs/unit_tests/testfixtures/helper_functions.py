
import json
from pathlib import Path

import numpy as np

from libs.dsp import DSP


def load_config_template():
    rel_configtemplate_path = Path("../server/libs")
    # Convert relative path to abs path.
    libs_folder = Path(rel_configtemplate_path).resolve()
    configtemplate_file = libs_folder / Path("config_template.json")

    if not Path.exists(configtemplate_file):
        error_msg = f'Could not find the template config file: "{configtemplate_file}"'
        raise FileNotFoundError(error_msg)

    # Read the Backup Config.
    with Path.open(configtemplate_file, "r") as read_file:
        try:
            return json.load(read_file)
        except json.JSONDecodeError:
            return None


def generate_random_demo_audiodata(config, device_config):
    dsp = DSP(config, device_config)
    rng = np.random.default_rng()
    random_audio_input = rng.integers(
        low=0, high=32767, size=config["general_settings"]["frames_per_buffer"], dtype="int16"
    )
    random_audio_input = random_audio_input.astype(np.float32)
    return dsp.update(random_audio_input)
