from file_utils import FileManager
from networking import Connector


def main():
    #FileManager.posterize_file('./test')
    Connector.broadcast_presence()


if __name__ == '__main__':
    main()
