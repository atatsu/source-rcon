import sys
import logging
import socket
import struct
import functools
from argparse import Namespace
import logging
LOG = logging.getLogger(__name__)

from tornado.ioloop import IOLoop

from srcrcon.connection import authenticate
from srcrcon.command import execute, Command
from srcrcon.args import parser


class SrcRCON:

    def __init__(self) -> None:
        self._interactive = False

    def _invoke_command(self, command_cls: Command, args: Namespace) -> None:
        pass

    def send_single_command(self, cmd, host, port, password):
        IOLoop.current().run_sync(lambda: self._single_command(cmd, host, port, password))

    async def _single_command(self, cmd, host, port, password):
        conn = await authenticate(password, host=host, port=port)
        cmd = Command(cmd)
        await execute(cmd, conn)
        conn.disconnect()

    def register_commands(
        self,
        *commands: Command,
        title: str = None,
        description: str = None,
        help: str = None
    ) -> None:
        subparsers = parser.add_subparsers(
            title=title,
            description=description,
            help=help,
        )

        for command in commands:
            # TODO: assert `name`
            subcommand = subparsers.add_parser(
                command.name,
                help=command.help
            )
            for arg in command.args:
                subcommand.add_argument(arg['name'], help=arg.get('help'))
            subcommand.set_defaults(func=functools.partial(self._invoke_command, command))

    def start(self) -> None:
        """
        Starts `SrcRCON`. This involves parsing any cli args that were passed
        and determining in which mode to run.
        """
        # TODO: read config
        if len(sys.argv) < 2:
            # TODO: only do this if no config found!
            parser.print_usage()
            sys.exit()

        args = parser.parse_args()

        if args.loglevel:
            logging.basicConfig(level=getattr(logging, args.loglevel.upper()))

        if args.command:
            self.send_single_command(args.command, args.host, args.port, args.password or '')
            sys.exit()
