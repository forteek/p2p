from os import rename
from os.path import getsize, abspath
from hashlib import sha256


class FileManager:
    @staticmethod
    def posterize_file(path: str) -> str:
        filename = path.split('/')[-1]
        size = getsize(path)
        file_hash = sha256()

        with open(f'./known_files/{filename}.temp', 'w') as known_file:
            known_file.writelines([
                abspath(path) + '\n',
                str(size) + '\n',
            ])

            with open(path, 'rb') as file:
                while True:
                    chunk: bytes = file.read(65536)
                    if not chunk:
                        break

                    known_file.write(sha256(chunk).hexdigest() + '\n')
                    file_hash.update(chunk)

            known_file.write(file_hash.hexdigest() + '\n')

        file_hash = file_hash.hexdigest()
        rename(f'./known_files/{filename}.temp', f'./known_files/{file_hash}')

        return file_hash
