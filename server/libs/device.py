from multiprocessing import Process, Queue

from loguru import logger

from libs.effect_service import EffectService
from libs.output_service import OutputService
from libs.queue_wrapper import QueueWrapper  # pylint: disable=E0611, E0401


class Device:
    def __init__(self, config, device_config, color_service_global) -> None:
        self.__config = config
        self.__device_config = device_config
        self.__color_service_global = color_service_global

        self.create_queues()
        self.create_processes()

    def start_device(self):
        logger.info(f'Starting device: {self.__device_config["device_name"]}')
        self.__output_process.start()
        self.__effect_process.start()

    def stop_device(self):
        logger.info(f'Stopping device: {self.__device_config["device_name"]}')
        try:
            self.__effect_process.terminate()
            self.__output_process.terminate()
        except AttributeError:
            pass

    def create_processes(self):
        self.__output_service = OutputService()
        self.__output_process = Process(
            target=self.__output_service.start,
            args=(self,)
        )

        self.__effect_service = EffectService()
        self.__effect_process = Process(
            target=self.__effect_service.start,
            args=(self,)
        )

    def create_queues(self):
        self.__device_notification_queue_in = QueueWrapper(Queue(2))
        self.__device_notification_queue_out = QueueWrapper(Queue(2))
        self.__effect_queue = QueueWrapper(Queue(2))
        self.__audio_queue = QueueWrapper(Queue(2))
        self.__output_queue = QueueWrapper(Queue(2))

    def refresh_config(self, config, device_config):
        logger.info(f'Refreshing config of device: {self.__device_config["device_name"]}')

        self.stop_device()

        self.__config = config
        self.__device_config = device_config

        self.create_queues()
        self.create_processes()

        self.__output_service = OutputService()
        self.__output_process = Process(
            target=self.__output_service.start,
            args=(self,)
        )

        self.__effect_service = EffectService()
        self.__effect_process = Process(
            target=self.__effect_service.start,
            args=(self,)
        )

        self.start_device()

    def get_config(self):
        return self.__config

    def get_device_config(self):
        return self.__device_config

    def get_device_notification_queue_in(self):
        return self.__device_notification_queue_in

    def get_device_notification_queue_out(self):
        return self.__device_notification_queue_out

    def get_effect_queue(self):
        return self.__effect_queue

    def get_audio_queue(self):
        return self.__audio_queue

    def get_output_queue(self):
        return self.__output_queue

    def get_color_service_global(self):
        return self.__color_service_global

    config = property(get_config)
    device_config = property(get_device_config)

    device_notification_queue_in = property(get_device_notification_queue_in)

    device_notification_queue_out = property(get_device_notification_queue_out)

    effect_queue = property(get_effect_queue)

    audio_queue = property(get_audio_queue)

    output_queue = property(get_output_queue)

    color_service_global = property(get_color_service_global)
