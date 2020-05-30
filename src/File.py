from os import path


class File:
    def __init__(self, file_path):
        self.__path = file_path
        self.__name = path.basename(self.__path)
        self.__size = path.getsize(self.__path)
        self.__jpg_name = ''
        self.__jpg_size = 0
        self.__jpg_percent = 0

    def get_path(self) -> str:
        return self.__path

    def get_name(self) -> str:
        return self.__name

    def get_size(self) -> int:
        return self.__size

    def set_jpg(self, path_name: str):
        self.__jpg_name = path_name
        self.__jpg_size = path.getsize(self.__jpg_name)

    def get_jpg_name(self) -> str:
        return path.basename(self.__jpg_name)

    def get_jpg_size(self) -> int:
        return self.__jpg_size

    def set_jpg_percent(self, jpg_percent: float):
        self.__jpg_percent = jpg_percent

    def get_jpg_percent(self) -> float:
        return self.__jpg_percent
