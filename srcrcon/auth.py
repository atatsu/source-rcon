import logging
LOG = logging.getLogger(__name__)
from typing import Optional

from .connection import Connection
from .protocol import AuthPacket, AuthResponsePacket
from .exceptions import AuthenticationFailure


class Auth:
    """
    Authenticates a `Connection`.
    """
    @property
    def authenticated(self) -> bool:
        return self._authenticated

    def __init__(self, password: str, conn: Connection) -> None:
        self._authenticated = False
        self._password = password
        self._conn = conn

    async def authenticate(self) -> Optional[Connection]:
        """
        Instruct the `Authenticator` to authenticate its `Connection`.

        :raises: `AuthenticationFailure`
        """
        auth = AuthPacket(self._password)
        await self._conn.send(auth)
        packet = await self._conn.read()

        if packet and isinstance(packet, AuthResponsePacket) and packet.id == auth.id:
            self._authenticated = True
            LOG.info('Authentication successful')
            return self._conn

        LOG.error('Authentication failed')
        raise AuthenticationFailure

