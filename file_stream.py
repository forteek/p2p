import socket

from message import MessageEvent, Message
from file_utils import FileReader, FileWriter, ChunkSizeCalculator
from networking import Peer, Socket
import socket
from time import sleep


class FileStream:
    def __init__(self, peer: Peer):
        self._socket = Socket()
        self._peer = peer

    def _punch_hole(self):
        while True:
            try:
                self._socket.write_raw(b'0', self._peer)
                self._socket.set_timeout(3)
                data, addr = self._socket.read_raw(1)
            except socket.timeout:
                print(f'Connection failed, retrying {self._socket._socket.getsockname()}')
                continue

            print(data)
            break


class OutboundFileStream(FileStream):
    def __init__(self, file_hash: str, peer: Peer):
        super().__init__(peer)
        self._file_hash = file_hash
        self._poster_path = f'./known_files/{file_hash}.ftl'
        self._file_path = self._get_file_path()
        self._chunk_size = ChunkSizeCalculator.calculate(self._file_path)

    def _get_file_path(self) -> str:
        line_generator = FileReader.read_lines(self._poster_path)
        file_path = next(line_generator)
        line_generator.close()

        return file_path

    def send(self):
        print(f'Sending {self._file_hash}')

        self._punch_hole()

        self._socket.write(
            Message(MessageEvent.CHUNK_SIZE, self._chunk_size),
            self._peer
        )

        for chunk in FileReader.read(self._file_path, self._chunk_size):
            self._socket.write_raw(chunk, self._peer)

        self._socket.write_raw(b'000', self._peer)
        print(f'{self._file_hash} sent')


class InboundFileStream(FileStream):
    def __init__(self, file_hash: str, file_path: str, peer: Peer):
        super().__init__(peer)
        self._file_hash = file_hash
        self._file_path = file_path
        self._chunk_size = None

    def receive(self):
        print(f'Receiving {self._file_path}')
        self._punch_hole()
        chunk_size: int = self._await_chunk_size()

        while True:
            data, addr = self._socket.read_raw(chunk_size)

            if data == b'000':
                break

            FileWriter.write(self._file_path, data)

        print(f'{self._file_path} received')

    def _await_chunk_size(self) -> int:
        chunk_size = None

        while True:
            data, addr = self._socket.read(1024)

            if data.event != MessageEvent.CHUNK_SIZE:
                continue

            chunk_size = int(data.content)
            break

        return chunk_size
