import functools
import logging
LOG = logging.getLogger(__name__)

from tornado import netutil
from tornado.iostream import IOStream
from tornado.testing import bind_unused_port

from srcrcon.connection import Connection


class ListenerMixin:

    socket = None
    listener = None
    port = None

    def make_listener(self):
        self.socket, self.port = bind_unused_port()
        netutil.add_accept_handler(self.socket, self._on_connected)

    def _on_connected(self, connection, address):
        LOG.debug('accepted connection')
        self.listener = IOStream(connection)


class ConnectionMixin:

    conn = None

    def setUp(self):
        super(ConnectionMixin, self).setUp()
        self.make_listener()
        self.conn = Connection('127.0.0.1', self.port)


class ListenerConnectionMixin(ListenerMixin, ConnectionMixin):

    async def make_listener_and_connect(self):
        await self.conn.connect()


class FuncToolsPartialMatcher:
    def __init__(self, func, *args, **kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def __eq__(self, other):
        if not isinstance(other, functools.partial):
            return False

        assert other.func == self.func, 'Expected func: {!r}, Actual func: {!r}'.format(self.func, other.func)
        assert other.args == self.args, 'Expected args: {!r}, Actual args: {!r}'.format(self.args, other.args)
        assert other.keywords == self.kwargs, 'Expected kwargs: {!r}, Actual kwargs {!r}'.format(self.kwargs, other.kwargs)
        return True
