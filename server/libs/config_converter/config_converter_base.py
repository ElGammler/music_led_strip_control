class ConfigConverterBase:
    def __init__(self) -> None:
        self.from_version = 0
        self.to_version = 0

    from_version = 0
    to_version = 0

    @staticmethod
    def upgrade(old_config):
        return old_config
