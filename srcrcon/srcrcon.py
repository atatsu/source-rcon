import sys
import logging
from functools import partial
from argparse import Namespace
from typing import Sequence
import logging
LOG = logging.getLogger(__name__)

from srcrcon.connection import authenticate, execute
from srcrcon.command import Command
from srcrcon.args import new_parser


class SrcRCON:

    def __init__(self) -> None:
        self._interactive = False
        self._parser = new_parser()

    async def _invoke_command(self, command_cls: Command, args: Namespace) -> None:
        # TODO: implement interactive
        if not self._interactive:
            await self._single_command(
                command_cls(args),
                args.host,
                args.port,
                args.password
            )

    async def _single_command(
        self,
        cmd: Command,
        host: str,
        port: int,
        password: str
    ) -> None:
        conn = await authenticate(password, host=host, port=port)
        await execute(cmd, conn)
        conn.disconnect()

    def register_commands(
        self,
        *commands: Command,
        title: str = None,
        description: str = None,
        help: str = None
    ) -> None:
        subparsers = self._parser.add_subparsers(
            title=title,
            description=description,
            help=help,
        )

        for command_cls in commands:
            # TODO: assert `name`
            # TODO: assert `command_cls` is subclass of Command
            subcommand = subparsers.add_parser(
                command_cls.name,
                help=command_cls.help
            )
            for arg in command_cls.args:
                subcommand.add_argument(arg['name'], help=arg.get('help'))
            subcommand.set_defaults(func=partial(self._invoke_command, command_cls))

    async def start(self, *args: Sequence[str]) -> None:
        """
        Starts `SrcRCON`. This involves parsing any cli args that were passed
        and determining in which mode to run.
        """
        # TODO: read config
        if not args and len(sys.argv) < 2:
            # TODO: only do this if no config found!
            self._parser.print_usage()
            sys.exit()

        if args:
            parsed_args = self._parser.parse_args(args)
        else:
            parsed_args = self._parser.parse_args()

        if parsed_args.loglevel:
            logging.basicConfig(level=getattr(logging, args.loglevel.upper()))

        func = parsed_args.func
        await func(parsed_args)
