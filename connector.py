from networking import Peer, Socket, TrackerManager
from file_utils import FileManager
from message import Message, MessageEvent
from file_stream import OutboundFileStream, InboundFileStream

class Connector:
    @staticmethod
    def connect(peer: Peer) -> None:
        sock = Socket()
        sock.ping(peer)

        while True:
            data, addr = sock.read(1024)
            print(data, addr)

    @staticmethod
    def seed():
        tracker_manager = TrackerManager()
        sock = Socket()

        for tracker in tracker_manager.trackers:
            for filename in FileManager.get_known_files():
                sock.write(
                    Message(MessageEvent.HAS, filename),
                    tracker
                )

        while True:
            data, peer = sock.read(1024)

            if data.event == MessageEvent.NEED:
                file_hash = data.content

                if file_hash not in FileManager.get_known_files():
                    continue

                OutboundFileStream(file_hash).send(peer)

    @staticmethod
    def get(file_hash: str):
        tracker_manager = TrackerManager()
        sock = Socket()

        for tracker in tracker_manager.trackers:
            sock.write(
                Message(MessageEvent.NEED, file_hash),
                tracker
            )

        while True:
            data, peer = sock.read(1024)

            if data.event == MessageEvent.HAS:
                file_hash = data.content

                InboundFileStream(file_hash, f'./{file_hash}').receive()
