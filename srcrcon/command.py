import logging
LOG = logging.getLogger(__name__)

from .utils import fancy
from .exceptions import InvalidCommandError


class Command:

    name = None
    help = None
    args = []
    command_text = None

    success = fancy('{command!r} succeeded.', fg='green')
    failure = fancy('{command!r} failed!', fg='red')
    response = fancy('{response}', fg='yellow')
    command = None

    def __init__(
        self,
        command: str = None,
        success: str = None,
        failure: str = None,
        response: str = None
    ) -> None:
        self.success = success or self.success
        self.failure = failure or self.failure
        self.response = response or self.response
        self.command = command or self.command

        if not self.command:
            raise InvalidCommandError('Expected a command string')

        self.success = self.success.format(command=self.command)
        self.failure = self.failure.format(command=self.command)

    def get_command_text(self, args) -> str:
        raise NotImplementedError

    def __str__(self) -> str:
        return str(self.command)

    def __repr__(self) -> str:
        return repr(self.command)
