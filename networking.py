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

    def ping(self, peer: Peer) -> None:
        self._socket.sendto(b'0', peer)

    def keep_alive(self, peer: Peer) -> None:
        self.ping(peer)

    def read(self, size: int) -> Tuple[Message, Peer]:
        message, addr = self._socket.recvfrom(size)
        message = MessageSerializer.deserialize(message)

        return message, Peer(addr[0], addr[1])

    def read_raw(self, size: int) -> Tuple[bytes, Peer]:
        message, addr = self._socket.recvfrom(size)

        return message, Peer(addr[0], addr[1])

    def write(self, message: Message, peer: Peer) -> None:
        self._socket.sendto(MessageSerializer.serialize(message), peer)

    def write_raw(self, content: bytes, peer: Peer) -> None:
        self._socket.sendto(content, peer)


class TrackerManager(Singleton):
    def __init__(self):
        self.trackers: List[Peer] = []
        for tracker in FileReader.read_lines('known_trackers'):
            host, port = tracker.split(':')
            self.trackers.append(Peer(host, int(port)))


class ConnectionManager(Singleton):
    def __init__(self):
        self.connections = []
