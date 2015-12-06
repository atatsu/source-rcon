import argparse


parser = argparse.ArgumentParser(
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description=('Source RCON client\nIf no command is specified %(prog)s will start '
                 'in interactive mode,\nkeeping the connection open allowing for '
                 'cotinued command input.')
)
parser.add_argument(
    'host',
    help='Host of server to connect to.'
)
parser.add_argument(
    '--port',
    type=int,
    default=27015,
    help='Port of server to connect to. (default: %(default)s)'
)
parser.add_argument(
    '-c',
    '--command',
    dest='command',
    help='Command to send via RCON protocol. %(prog)s will exit once command completes.'
)

parser.add_argument(
    '-p',
    '--password',
    dest='password',
    help=('Password to authenticate with. Be mindful of using this flag as '
          "anyone with access to the system's process list will see the password.")
)
