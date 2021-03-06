import socket
from model import Singleton
from typing import Tuple, List
from message import Message, MessageSerializer
from typing import NamedTuple
from file_utils import FileReader


class Peer(NamedTuple):
    host: str
    port: int


class Socket(Singleton):
    def __init__(self):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._socket.bind(('', 62010))

    def ping(self, peer: Peer) -> None:
        self._socket.sendto(b'0', peer)

    def keep_alive(self, peer: Peer) -> None:
        self.ping(peer)

    def bind(self, address: Peer) -> None:
        self._socket.bind(address)

    def set_timeout(self, time: int) -> None:
        self._socket.settimeout(time)

    def read(self, size: int) -> Tuple[Message, Peer]:
        message, addr = self._socket.recvfrom(size)
        print(f'Received {message} from {addr}')
        message = MessageSerializer.deserialize(message)

        return message, Peer(addr[0], addr[1])

    def read_raw(self, size: int) -> Tuple[bytes, Peer]:
        message, addr = self._socket.recvfrom(size)
        print(f'Received {message} from {addr}')

        return message, Peer(addr[0], addr[1])

    def write(self, message: Message, peer: Peer) -> None:
        self.write_raw(MessageSerializer.serialize(message), peer)

    def write_raw(self, content: bytes, peer: Peer) -> None:
        self._socket.sendto(content, peer)
        print(f'Sent {content} to {peer}')


class TrackerManager(Singleton):
    def __init__(self):
        self.trackers: List[Peer] = []
        for tracker in FileReader.read_lines('known_trackers'):
            host, port = tracker.split(':')
            self.trackers.append(Peer(host, int(port)))


class ConnectionManager(Singleton):
    def __init__(self):
        self.connections = []
