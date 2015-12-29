import sys
from asyncio import coroutine
from functools import partial
from argparse import Namespace
from configparser import ConfigParser
from typing import Sequence
import logging
LOG = logging.getLogger(__name__)

from tornado.ioloop import IOLoop

from srcrcon.connection import authenticate, execute
from srcrcon.command import Command, Argument
from srcrcon.args import new_parser
from srcrcon.exceptions import MissingHostError


class SrcRCON:

    def __init__(self) -> None:
        self._interactive = False
        self._config = ConfigParser()
        self._parser = new_parser()

    def _read_config(self, parsed_args: Namespace) -> None:
        # separate the config file name from the section name
        try:
            configfile, section = parsed_args.config.split('=')
        except ValueError:
            configfile, section = parsed_args.config, None

        self._config.read(configfile)

        allowed = ['host', 'port', 'password']
        new_args = []
        # build an args list to send through the parser pulling values
        # from the config if they exist
        # TODO: if no `section` specified default to only section
        # TODO: catch `MissingSectionHeaderError`
        section_opts = self._config[section]
        for opt in section_opts:
            if opt not in allowed:
                continue

            val = section_opts.get(opt)
            if val:
                new_args.extend(['--{}'.format(opt), val])

        self._parser.parse_args(new_args, namespace=parsed_args)


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
            # TODO: assert `command_cls` is subclass of Command
            subcommand = subparsers.add_parser(
                command_cls.__name__.lower(),
                help=command_cls.__doc__ or ''
            )

            for arg_attr in command_cls._arguments:
                subcommand.add_argument(
                    arg_attr.get_name(),
                    help=arg_attr.__doc__
                )

            subcommand.set_defaults(func=partial(self._invoke_command, command_cls))

    async def init(self, *args: Sequence[str]) -> None:
        """
        Initializes `SrcRCON`. This involves parsing any cli args that were passed
        and determining in which mode to run.
        """
        if not args and len(sys.argv) < 2:
            # TODO: only do this if no config found!
            self._parser.print_usage()
            sys.exit()

        if args:
            parsed_args = self._parser.parse_args(args)
        else:
            parsed_args = self._parser.parse_args()

        if parsed_args.loglevel:
            logging.getLogger().setLevel(getattr(logging, parsed_args.loglevel.upper()))
        LOG.debug('parsed args: %s', parsed_args)

        # check if a config file was specified and if so load it
        if parsed_args.config:
            LOG.debug('config specified, attempting to parse %r', parsed_args.config)
            self._read_config(parsed_args)

        # verify we have a host and port to connect to
        if not getattr(parsed_args, 'host', None):
            raise MissingHostError(
                'No host specified. Use either the `--host` option or specify a config '
                'file with the `-c` option'
            )

        # FIXME: print help if `func` not present or assume interactive mode?
        func = parsed_args.func
        await func(parsed_args)

    def start(self) -> None:
        IOLoop.current().run_sync(self.init)
