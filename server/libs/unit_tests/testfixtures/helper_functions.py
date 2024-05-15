
import json
import os
import sys

import numpy as np

from libs.dsp import DSP


def load_config_template():
    rel_configtemplate_path = "../server/libs"
    # Convert relative path to abs path.
    libs_folder = os.path.abspath(rel_configtemplate_path) + "/"
    configtemplate_file = libs_folder + "config_template.json"

    if not os.path.exists(configtemplate_file):
        raise Exception(f'Could not find the template config file: "{configtemplate_file}"')

    # Read the Backup Config.
    with open(configtemplate_file, "r") as read_file:
        config_template = json.load(read_file)

    return config_template


def generate_random_demo_audiodata(config, device_config):
    dsp = DSP(config, device_config)
    random_audio_input = np.random.randint(
        low=0, high=32767, size=config["general_settings"]["frames_per_buffer"], dtype="int16")
    random_audio_input = random_audio_input.astype(np.float32)
    return dsp.update(random_audio_input)
