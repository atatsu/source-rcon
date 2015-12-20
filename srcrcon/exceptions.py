class SrcRconError(Exception):
    """
    Base exception for srcrcon.
    """


class MissingHostError(SrcRconError):
    """
    Raised when no host is specified.
    """


class ConnectionError(SrcRconError):
    """
    Raised when a connection attempt fails.
    """
    def __init__(self, host: str, port: int) -> None:
        self.host = host
        self.port = port

    def __str__(self) -> None:
        return repr((self.host, self.port))


class AuthenticationError(SrcRconError):
    """
    Raised when an authentication attempt fails.
    """


class InvalidCommandError(SrcRconError):
    """
    Raised when a `Command` is created with an invalid command string.
    """


class CommandError(SrcRconError):
    """
    Raised when a `Command` fails to execute properly.
    """
