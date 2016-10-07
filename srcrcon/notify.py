from abc import ABCMeta, abstractmethod


class Notifier(metaclass=ABCMeta):

    def __init__(self, mode: int) -> None:
        self.mode = mode

    @abstractmethod
    def notify(self, msg: str) -> None:
        pass


class ConsoleNotifier(Notifier):

    def notify(self, msg: str) -> None:
        print(msg)
