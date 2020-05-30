from src.Constants import FOLDER_NAME_OUTPUT_JPG
from src.File import File
from typing import List
from os import path
import glob


class Config:
    def __init__(self, work_path: str, work_extension: str, keep_results: bool = False):
        self.__work_path = path.join(work_path, '')
        self.__work_extension = work_extension
        self.__keep_results = keep_results
        self.__jpg_path = path.join(self.__work_path + FOLDER_NAME_OUTPUT_JPG, '')
        self.__work_files = self.__get_folder_content()
        self.__work_count = len(self.__work_files)

    def __get_folder_content(self) -> List[File]:
        content_list = []
        if self.path_exist():
            content_list = [File(item) for item in glob.glob('{}*.{}'.format(self.__work_path, self.__work_extension))]

        return content_list

    def path_exist(self) -> bool:
        return path.exists(self.__work_path)

    def get_work_path(self) -> str:
        return self.__work_path

    def get_work_extension(self) -> str:
        return self.__work_extension

    def keep_results(self) -> bool:
        return self.__keep_results

    def get_jpg_path(self) -> str:
        return self.__jpg_path

    def get_work_files(self) -> List[File]:
        return self.__work_files

    def get_work_count(self) -> int:
        return self.__work_count
