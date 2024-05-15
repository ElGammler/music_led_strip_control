import queue

from loguru import logger


class QueueWrapper:
    def __init__(self, queue) -> None:
        self.queue = queue

    def put_blocking(self, element):
        self.queue.put(element, block=True)

    def put_none_blocking(self, element):
        if self.queue.full():
            self.__delete_last_element()
        self.queue.put(element, block=True, timeout=0.033)

    def get_blocking(self):
        return self.queue.get(block=True)

    def get_blocking_with_timeout(self):
        # return self.queue.get(block=True, timeout=1)
        try:
            return self.queue.get(block=True, timeout=1)
        except queue.Empty:
            logger.debug("Could not get item from queue, queue is empty.")
            return None

    def get_none_blocking(self):
        return self.queue.get(block=True, timeout=0.033)

    def empty(self):
        return self.queue.empty()

    def full(self):
        return self.queue.full()

    def __delete_last_element(self):
        try:
            delete_element = self.get_none_blocking()
            del delete_element
        except Exception as e:
            logger.debug(f"Could not delete element from queue: {e}")
