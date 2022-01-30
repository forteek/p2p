from file_utils import FileManager
from connector import Connector
import sys


def main():
    if sys.argv[1] == 'posterize':
        FileManager.posterize_file(sys.argv[2])

    elif sys.argv[1] == 'seed':
        Connector.seed()

    elif sys.argv[1] == 'get':
        Connector.get(sys.argv[2])


if __name__ == '__main__':
    main()
