class SrcRconError(Exception):
    """
    Base exception for srcrcon.
    """


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
