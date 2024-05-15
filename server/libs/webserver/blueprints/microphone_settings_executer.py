import re
import subprocess
from sys import platform

from libs.webserver.executer_base import ExecuterBase
from loguru import logger


class MicrophoneSettingsExecuter(ExecuterBase):
    def microphone_get_volume(self) -> dict:
        """Return information about the microphone volume."""
        result = {}
        try:
            process = subprocess.run(
                ["/usr/bin/amixer", "get", "Mic"],
                text=True,
                capture_output=True,
                check=False
            )

            result["output"] = process.stdout
            result["error"] = process.stderr
            result["returncode"] = process.returncode
            result["level"] = self.get_level_form_output(result["output"])

        except Exception:
            logger.exception("Unknown error.")
            if platform == "linux":
                logger.exception("Exeception during mic level down.")
            result["level"] = 0
            result["output"] = ""
            result["error"] = "Could not change set mic volume."
            result["returncode"] = 1

        return result

    def microphone_set_volume(self, level: str) -> dict:
        """Set the microphone volume."""
        result = {}
        try:
            process = subprocess.run(
                ["/usr/bin/amixer", "set", "Mic", f"{level}%"],
                text=True,
                capture_output=True,
                check=False
            )

            result["output"] = process.stdout
            result["error"] = process.stderr
            result["returncode"] = process.returncode

        except Exception:
            logger.exception("Exeception during mic level up.")
            result["output"] = ""
            result["error"] = "Could not change set mic volume."
            result["returncode"] = 1

        return result

    def get_level_form_output(self, output: str) -> int:
        """Get the level from the output of the amixer command."""
        if output is None or not output:
            return 0

        level = 0

        x = re.search(r"(\d+)?%", output)
        try:
            level = int(x.group(1))
        except Exception:
            logger.exception("Could not get mic level.")

        return level
