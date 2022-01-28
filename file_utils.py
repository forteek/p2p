from os import rename
from os.path import getsize, abspath
from hashlib import sha256
from typing import Iterator


class FileManager:
    @staticmethod
    def posterize_file(path: str) -> str:
        filename = path.split('/')[-1]
        size = getsize(path)
        file_hash = sha256()

        with open(f'./known_files/{filename}.ftl.temp', 'w') as known_file:
            known_file.writelines([
                abspath(path) + '\n',
                str(size) + '\n',
            ])

            for chunk in FileReader.read(path):
                known_file.write(sha256(chunk).hexdigest() + '\n')
                file_hash.update(chunk)

            known_file.write(file_hash.hexdigest() + '\n')

        file_hash = file_hash.hexdigest()
        rename(f'./known_files/{filename}.ftl.temp', f'./known_files/{file_hash}.ftl')

        return file_hash


class FileReader:
    @staticmethod
    def read(path: str) -> Iterator[bytes]:
        with open(path, 'rb') as file:
            while True:
                chunk: bytes = file.read(1048576)
                if not chunk:
                    break

                yield chunk
