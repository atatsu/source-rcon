import logging
LOG = logging.getLogger(__name__)

from .protocol import ExecCommandPacket, ResponseValuePacket
from .connection import Connection


class Command:

    success = None
    failure = None
    command = None

    def __init__(
        self,
        command: str = None,
        success: str = None,
        failure: str = None
    ) -> None:
        self.success = success or self.success
        self.failure = failure or self.failure
        self.command = command or self.command
        # TODO: assert `command` set

    def __str__(self) -> str:
        return self.command


async def execute(cmd: Command, conn: Connection) -> str:
    # TODO: assert connection active
    # TODO: assert connection authenticated
    LOG.info('Executing command: %s', cmd)
    request = ExecCommandPacket(str(cmd))
    await conn.send(request)

    response = await conn.read()

    if (not response
            or not isinstance(response, ResponseValuePacket)
            or response.id != request.id
        ):
        raise NotImplementedError

    LOG.info('Command %r successful', cmd)
    print(cmd.success)
    return True
