from loguru import logger

from libs.outputs.output import Output


class OutputDummy(Output):
    def __init__(self, device) -> None:
        # Call the constructor of the base class.
        super().__init__(device)

    @staticmethod
    def show(output_array) -> None:
        logger.debug(f"Output dummy... {output_array}")
