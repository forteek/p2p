import socket
from model import Singleton
from file_utils import FileReader, FileManager
from typing import Tuple
from message import Message, MessageSerializer, MessageEvent


class Socket(Singleton):
    def __init__(self):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def ping(self, peer: Tuple[str, int]) -> None:
        self._socket.sendto(b'0', peer)

    def keep_alive(self, peer: Tuple[str, int]) -> None:
        self.ping(peer)

    def read(self, size: int) -> Tuple[Message, Tuple[str, int]]:
        message, peer = self._socket.recvfrom(size)
        message = MessageSerializer.deserialize(message)

        return message, peer

    def write(self, message: Message, peer: Tuple[str, int]) -> None:
        self._socket.sendto(MessageSerializer.serialize(message), peer)


class TrackerManager(Singleton):
    def __init__(self):
        self.trackers = []
        for tracker in FileReader.read_lines('known_trackers'):
            host, port = tracker.split(':')
            self.trackers.append((host, int(port)))


class ConnectionManager(Singleton):
    def __init__(self):
        self.connections = []


class Connector:
    @staticmethod
    def connect(peer: Tuple[str, int]) -> None:
        sock = Socket()
        sock.ping(peer)

        while True:
            data, addr = sock.read(1024)
            print(data, addr)

    @staticmethod
    def broadcast_presence():
        tracker_manager = TrackerManager()
        sock = Socket()

        for tracker in tracker_manager.trackers:
            for filename in FileManager.get_known_files():
                sock.write(
                    Message(MessageEvent.OFFER, filename),
                    tracker
                )
