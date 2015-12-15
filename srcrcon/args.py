import argparse


def new_parser():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=('Source RCON client\nIf no command is specified %(prog)s will start '
                    'in interactive mode,\nkeeping the connection open allowing for '
                    'cotinued command input.')
    )
    parser.add_argument(
        '--host',
        help='Host of server to connect to.'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=27015,
        help='Port of server to connect to. (default: %(default)s)'
    )
    parser.add_argument(
        '--password',
        dest='password',
        help=('Password to authenticate with. Be mindful of using this flag as '
            "anyone with access to the system's process list will see the password.")
    )
    parser.add_argument(
        '--logging',
        choices=('debug', 'info', 'warn', 'error'),
        dest='loglevel',
        help='Enable logging output.'
    )

    parser.add_argument(
        '-c',
        '--config',
        dest='config',
        help='Config file to read options from.'
    )

    return parser
