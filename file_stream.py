from message import MessageEvent
from file_utils import FileReader, FileWriter, ChunkSizeCalculator
from networking import Peer, Socket


class OutboundFileStream:
    def __init__(self, file_hash: str):
        self._file_hash = file_hash
        self._poster_path = f'./known_files/{file_hash}.ftl'
        self._file_path = self._get_file_path()
        self._chunk_size = ChunkSizeCalculator.calculate(self._file_path)
        self._socket = Socket()

    def _get_file_path(self) -> str:
        line_generator = FileReader.read_lines(self._poster_path)
        file_path = next(line_generator)
        line_generator.close()

        return file_path

    def send(self, peer: Peer):
        print(f'Sending {self._file_hash}')

        for chunk in FileReader.read(self._file_path, self._chunk_size):
            self._socket.write_raw(chunk, peer)

        self._socket.write_raw(b'000', peer)
        print(f'{self._file_hash} sent')


class InboundFileStream:
    def __init__(self, file_hash: str, file_path: str):
        self._file_hash = file_hash
        self._file_path = file_path
        self._chunk_size = None
        self._socket = Socket()

    def receive(self):
        print(f'Receiving {self._file_path}')
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
