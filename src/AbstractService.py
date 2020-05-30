from os import makedirs
from src.Config import Config
from shutil import rmtree
import logging


class AbstractService:
    @staticmethod
    def create_dir(directory: str):
        makedirs(directory)

    @staticmethod
    def delete_dir(directory: str):
        rmtree(directory)

    @staticmethod
    def is_valid_config(configurator: Config) -> bool:
        """Checks if configurator is valid

        :param Config configurator:
        :return:
        """
        if not configurator.path_exist():
            logging.error("Work Folder '{}' does not exist!".format(configurator.get_work_path()))
            return False

        if configurator.get_work_count() == 0:
            logging.error("Work Folder '{}' doesn't have any {} image!".format(
                configurator.get_work_path(),
                configurator.get_work_extension().upper()
            ))
            return False

        return True
