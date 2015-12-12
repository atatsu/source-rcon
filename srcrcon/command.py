import logging
LOG = logging.getLogger(__name__)

from .utils import fancy
from .protocol import ExecCommandPacket, ResponseValuePacket
from .connection import Connection
from .exceptions import InvalidCommandError, CommandError


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


async def execute(cmd: Command, conn: Connection) -> str:
    # TODO: assert connection active
    # TODO: assert connection authenticated
    LOG.info('Executing command: %r', cmd)
    request = ExecCommandPacket(str(cmd))
    await conn.send(request)

    response = await conn.read()

    if (not response
            or not isinstance(response, ResponseValuePacket)
            or response.id != request.id
        ):
        LOG.warning('Command %r failed', cmd)
        print(cmd.failure)
        # TODO: catch this somewhere and fancy print it like command successes get printed
        raise CommandError

    LOG.info('Command %r successful', cmd)
    LOG.debug('server response: %s', response.body)
    print(cmd.success)
    print(cmd.response.format(response=response.body))
