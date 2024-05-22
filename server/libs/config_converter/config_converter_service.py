from libs.config_converter.config_converter_v2 import ConfigConverterV2
from libs.config_converter.config_converter_v3 import ConfigConverterV3


class ConfigConverterService:
    def __init__(self) -> None:
        pass

    @staticmethod
    def upgrade(old_config):
        config_converter_v2 = ConfigConverterV2()
        config_converter_v3 = ConfigConverterV3()

        # Convert to the newer config version.
        if "version" not in old_config:
            old_config = config_converter_v2.upgrade(old_config)

        if old_config["version"] < 2:
            old_config = config_converter_v2.upgrade(old_config)

        if old_config["version"] < 3:
            old_config = config_converter_v3.upgrade(old_config)

        return old_config
