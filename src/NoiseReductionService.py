from src.AbstractService import AbstractService
from src.Config import Config


class NoiseReductionService(AbstractService):
    def execute(self, configurator: Config):
        """Core

        :param Config configurator:
        :return:
        """
        print(' - IMAGE NOISE REDUCTION CLASSIFIER - ')

        if not self.is_valid_config(configurator):
            exit(1)

        print("Work folder: '{}'.".format(configurator.get_work_path()))
        print("Found {} {} images.".format(configurator.get_work_count(), configurator.get_work_extension().upper()))
