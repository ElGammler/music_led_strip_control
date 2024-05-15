from loguru import logger

from libs.outputs.output import Output  # pylint: disable=E0611, E0401


class OutputDummy(Output):
    def __init__(self, device) -> None:
        # Call the constructor of the base class.
        super().__init__(device)

    def show(self, output_array):
        logger.debug("Output dummy...")
