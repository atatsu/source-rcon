from argparse import Namespace
from abc import ABCMeta, abstractmethod
import logging
LOG = logging.getLogger(__name__)

from .utils import fancy


# TODO: add a metaclass that asserts the various attributes of the subclasses are valid
class Command(metaclass=ABCMeta):

    #: Name of the command. This is the value that gets added to
    #: the parser and used as an actual subcommand.
    name = None
    #: Help text for the parser subcommand.
    help = None
    #: Arguments for the subcommand. These get added to the subcommand
    #: parser arguments. list(dict(name='arg name', help='arg help'))
    args = []
    #: Actual text for the command. Args parsed from subcommand will be passed
    #: in as a `string.format` so use tokens that match `Command.args`.
    command_fmt = None

    #: Message to display upon command success. Formatting will be applied
    #: with the command text so include a `{command_text}` token
    #: if you want it as part of the resulting string.
    success_fmt = fancy('{command_text!r} succeeded.', fg='green')
    #: Message to display upon command failure. Formatting will be applied
    #: with the command text so include a `{command_text}` token
    #: if you want it as part of the resulting string.
    failure_fmt = fancy('{command_text!r} failed!', fg='red')
    #: Response from the server. Formatting will be applied with the server's
    #: response so include a `{response}` token if you want it as part of the
    #: resulting string.
    response_fmt = fancy('{response}', fg='yellow')

    def __init__(self, parsed_args: Namespace) -> None:
        self._args = parsed_args

    def success(self) -> str:
        return self.success_fmt.format(command_text=str(self))

    def failure(self) -> str:
        return self.failure_fmt.format(command_text=str(self))

    def response(self, response: str):
        return self.response_fmt.format(response=response)

    @abstractmethod
    def validate(self, response: str) -> bool:
        return True

    def __str__(self) -> str:
        return self.command_fmt.format(**vars(self._args))

    def __repr__(self) -> str:
        return repr(self.command_fmt.format(**vars(self._args)))

    def __eq__(self, other) -> bool:
        return (
            isinstance(other, Command) and
            self.name == other.name and
            self.help == other.help and
            self.args == other.args and
            self.command_fmt == other.command_fmt and
            self.success_fmt == other.success_fmt and
            self.failure_fmt == other.failure_fmt and
            self.response_fmt == other.response_fmt
        )
