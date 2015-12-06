import logging
LOG = logging.getLogger(__name__)

import colorama
from colorama import Fore, Back, Style

from .protocol import ExecCommandPacket, ResponseValuePacket
from .connection import Connection
from .exceptions import InvalidCommandError, CommandError

_color_mapping = dict(
    fgblack=Fore.BLACK,
    fgred=Fore.RED,
    fggreen=Fore.GREEN,
    fgyellow=Fore.YELLOW,
    fgblue=Fore.BLUE,
    fgmagenta=Fore.MAGENTA,
    fgcyan=Fore.CYAN,
    fgwhite=Fore.WHITE,
    bgblack=Back.BLACK,
    bgred=Back.RED,
    bggreen=Back.GREEN,
    bgyellow=Back.YELLOW,
    bgblue=Back.BLUE,
    bgmagenta=Back.MAGENTA,
    bgcyan=Back.CYAN,
    bgwhite=Back.WHITE,
    sdim=Style.DIM,
    snormal=Style.NORMAL,
    sbright=Style.BRIGHT,
)


def fancy(text: str, fg: str = None, bg: str = None, style: str = None) -> str:
    if not fancy._initialized:
        colorama.init()
        fancy._initialized = True

    reset = Style.RESET_ALL if fg or bg or style else ''
    fg = _color_mapping.get('fg{}'.format(fg), '')
    bg = _color_mapping.get('bg{}'.format(bg), '')
    style = _color_mapping.get('s{}'.format(style), '')

    text = '{fg}{bg}{style}{text}{reset}'.format(
        fg=fg,
        bg=bg,
        style=style,
        text=text,
        reset=Style.RESET_ALL,
    )

    return text
fancy._initialized = False


class Command:

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
        raise CommandError

    LOG.info('Command %r successful', cmd)
    LOG.debug('server response: %s', response.body)
    print(cmd.success)
    print(cmd.response.format(response=response.body))
