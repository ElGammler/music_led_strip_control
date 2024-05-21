class Output:
    def __init__(self, device) -> None:
        self._device = device
        self._device_config = device.device_config

    @staticmethod
    def show(output_array) -> None:
        msg = f"Please implement this method. {output_array}"
        raise NotImplementedError(msg)
