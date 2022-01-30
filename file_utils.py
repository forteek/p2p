import os
from os.path import getsize, abspath
from hashlib import sha256
from typing import Generator


class FileManager:
    @staticmethod
    def posterize_file(path: str) -> str:
        filename = path.split('/')[-1]
        size = getsize(path)
        chunk_size = ChunkSizeCalculator.calculate(path)
        file_hash = sha256()

        with open(f'./known_files/{filename}.ftl.temp', 'w') as known_file:
            known_file.writelines([
                abspath(path) + '\n',
                str(size) + '\n',
            ])

            for chunk in FileReader.read(path, chunk_size):
                known_file.write(sha256(chunk).hexdigest() + '\n')
                file_hash.update(chunk)

            known_file.write(file_hash.hexdigest() + '\n')

        file_hash = file_hash.hexdigest()
        os.rename(f'./known_files/{filename}.ftl.temp', f'./known_files/{file_hash}.ftl')

        return file_hash

    @staticmethod
    def get_known_files() -> Generator[str, None, None]:
        for file in os.listdir('known_files'):
            filename, extension = file.split('.')
            if extension == 'ftl':
                yield filename


class FileReader:
    @staticmethod
    def read(path: str, chunk_size: int) -> Generator[bytes, None, None]:
        with open(path, 'rb') as file:
            while True:
                chunk: bytes = file.read(chunk_size)
                if not chunk:
                    break

                yield chunk

    @staticmethod
    def read_lines(path: str) -> Generator[str, None, None]:
        with open(path, 'r') as file:
            while True:
                line: str = file.readline().strip()
                if not line:
                    break

                yield line


class FileWriter:
    @staticmethod
    def write(path: str, content: bytes):
        with open(path, 'ab') as file:
            file.write(content)


class ChunkSizeCalculator:
    @staticmethod
    def calculate(filepath: str):
        size = getsize(filepath)

        return min(int(size / 10), 1048576) or 1
