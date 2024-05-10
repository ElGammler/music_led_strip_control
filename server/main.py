# Main File
# ----------------
#
# The program will start here.
# This file will only initialize and start the processes.

import sys
from sys import platform, version_info

if version_info < (3, 9):  # noqa: UP036
    sys.exit("\033[91mError: MLSC requires Python 3.9 or greater.")

import logging
import subprocess
from multiprocessing import Lock, Process, Queue
from time import sleep

import pyaudio
from libs.audio_process_service import AudioProcessService
from libs.config_service import ConfigService
from libs.device_manager import DeviceManager
from libs.notification_service import NotificationService
from libs.webserver.webserver import Webserver

if platform == "linux":
    import fcntl
import os


def instance_already_running():
    """Detect if an an instance is already running, globally at the operating system level.

    Using `os.open` ensures that the file pointer won't be closed
    by Python's garbage collector after the function's scope is exited.

    The lock will be released when the program exits, or could be
    released if the file pointer were closed.
    """
    lock_path = "../default.lock"

    try:
        lock_file_pointer = os.open(lock_path, os.O_WRONLY | os.O_CREAT)
    except PermissionError:
        sys.exit("\033[91mError: Run MLSC as root (sudo).")

    try:
        fcntl.lockf(lock_file_pointer, fcntl.LOCK_EX | fcntl.LOCK_NB)
        return False
    except OSError:
        return True


if platform == "linux" and instance_already_running():
    x = subprocess.Popen(
        ["/usr/bin/systemctl", "is-active", "mlsc"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        shell=False,
        text=True
    )
    systemctl_status = x.communicate()[0].strip()
    if systemctl_status == "active":
        sys.exit("\033[91mError: MLSC is already running as a service.\nStop the running service with 'sudo systemctl stop mlsc'.")
    else:
        sys.exit("\033[91mError: MLSC is already running directly.\nStop the running instance with 'CTRL+C'.")


class Main:
    """Main class. It controls everything.

    It's the first starting point of the program.
    """

    def start(self):
        """Start all necessary components."""
        # We need a lock to prevent too fast saving and loading actions of the config
        self._config_lock = Lock()

        # Create the instance of the config
        self._config_instance = ConfigService.instance(self._config_lock)
        self._config = self._config_instance.config

        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing MLSC...")

        # Check config compatibility
        self._config_instance.check_compatibility()

        # Init pyaudio
        self._py_audio = pyaudio.PyAudio()

        # Prepare the queue for the output
        self._output_queue = Queue(2)
        self._effects_queue = Queue(100)
        self._audio_queue = Queue(2)

        # Prepare all notification queues
        self._notification_queue_audio_in = Queue(100)
        self._notification_queue_audio_out = Queue(100)

        self._notification_queue_device_manager_in = Queue(100)
        self._notification_queue_device_manager_out = Queue(100)

        self._notification_queue_webserver_in = Queue(100)
        self._notification_queue_webserver_out = Queue(100)

        # Start the DeviceManager Service
        self._device_manager = DeviceManager()
        self._device_manager_process = Process(
            target=self._device_manager.start,
            args=(
                self._config_lock,
                self._notification_queue_device_manager_in,
                self._notification_queue_device_manager_out,
                self._effects_queue,
                self._audio_queue,
            ))
        self._device_manager_process.start()

        # Start Notification Service
        self._notification_service = NotificationService()
        self._notification_service_process = Process(
            target=self._notification_service.start,
            args=(
                self._config_lock,
                self._notification_queue_device_manager_in,
                self._notification_queue_device_manager_out,
                self._notification_queue_audio_in,
                self._notification_queue_audio_out,
                self._notification_queue_webserver_in,
                self._notification_queue_webserver_out,
            ))
        self._notification_service_process.start()

        # Start Webserver
        self._webserver = Webserver()
        self._webserver_process = Process(
            target=self._webserver.start,
            args=(
                self._config_lock,
                self._notification_queue_webserver_in,
                self._notification_queue_webserver_out,
                self._effects_queue,
                self._py_audio
            ))
        self._webserver_process.start()

        # Start audio process
        self._audio = AudioProcessService()
        self._audio_process = Process(
            target=self._audio.start,
            args=(
                self._config_lock,
                self._notification_queue_audio_in,
                self._notification_queue_audio_out,
                self._audio_queue,
                self._py_audio
            ))
        self._audio_process.start()

        self.logger.info("Initialization finished.")

        try:
            self.logger.info("MLSC started...")

            self._cancel_token = False

            # Do nothing with this thread. Just wait for the exit.
            while not self._cancel_token:
                sleep(10)

        except KeyboardInterrupt:
            self.logger.info("Stopping MLSC...")
            self._notification_service_process.terminate()
            self._webserver_process.terminate()
            self.logger.info("MLSC stopped")


if __name__ == "__main__":

    main = Main()
    main.start()
