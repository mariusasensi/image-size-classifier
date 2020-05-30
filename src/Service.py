from os import makedirs, path
from PIL import Image
from shutil import rmtree, copyfile
from src.Config import Config
from src.Constants import IMAGE_FORMAT_JPG, PERCENT_TIERS, FOLDER_NAME_OUTPUT_RESULT, IMAGE_FORMAT_JPEG
from src.File import File
from typing import List, Dict
import glob
import logging
import matplotlib.pyplot as plt


class Service:
    def execute(self, configurator: Config):
        """Core

        :param Config configurator:
        :return:
        """
        if not self.is_valid_config(configurator):
            exit(1)

        print("Work folder: '{}'.".format(configurator.get_work_path()))
        print("Found {} {} images.".format(configurator.get_work_count(), configurator.get_work_extension().upper()))
        print("JPG folder: '{}'.".format(configurator.get_jpg_path()))

        if not self.is_already_worked(configurator):
            self.create_dir(path.dirname(configurator.get_jpg_path()))
            iter_max = configurator.get_work_count()
            counter = 1

            print('[START] Conversion {} to {}.'.format(configurator.get_work_extension().upper(), IMAGE_FORMAT_JPG))
            for work_file in configurator.get_work_files():
                jpg_path = '{}{}.{}'.format(configurator.get_jpg_path(), work_file.get_name(), IMAGE_FORMAT_JPG.lower())
                print("[{}/{}] Converting: '{}' -> '{}'".format(counter, iter_max, work_file.get_path(), jpg_path))
                self.to_jpg(work_file.get_path(), jpg_path)
                work_file.set_jpg(jpg_path)
                counter += 1
            print('[END] Conversion {} to {}.'.format(configurator.get_work_extension().upper(), IMAGE_FORMAT_JPG))
        else:
            print('Work already done has been found in this directory!')
            for work_file in configurator.get_work_files():
                jpg_path = '{}{}.{}'.format(configurator.get_jpg_path(), work_file.get_name(), IMAGE_FORMAT_JPG.lower())
                work_file.set_jpg(jpg_path)

        print('Successfully generated {} images!'.format(configurator.get_work_extension().upper()))
        values = [file.get_jpg_size() for file in configurator.get_work_files()]
        minimum = min(values)
        maximum = max(values)

        if (maximum - minimum) == 0:
            logging.error('All images have the same size!')
            exit(1)

        tiers = PERCENT_TIERS
        for file in configurator.get_work_files():
            image_percent = round(((file.get_jpg_size() - minimum) * 100 / (maximum - minimum)), 4)
            file.set_jpg_percent(image_percent)
            self.classifier_tiers(tiers, image_percent)

        plot = self.generate_plot(configurator.get_work_files())
        self.interface(configurator, plot, tiers)

        if not configurator.keep_results():
            print("Deleting '{}' path...".format(configurator.get_jpg_path()))
            self.delete_dir(configurator.get_jpg_path())
        else:
            print("Folder '{}' hasn't been deleted because it has been decided to keep it for future runs.".format(
                configurator.get_jpg_path()))

    def is_already_worked(self, configuration: Config) -> bool:
        """Checks if the process already runs in this work directory.

        :param Config configuration:
        :return:
        """
        if not path.exists(configuration.get_jpg_path()):
            return False

        jpg_files = [path.splitext(path.basename(jpg))[0] for jpg in
                     glob.glob('{}*.{}'.format(configuration.get_jpg_path(), IMAGE_FORMAT_JPG.lower()))]
        work_files = [file.get_name() for file in configuration.get_work_files()]

        same = jpg_files.sort() == work_files.sort()
        if not same:
            self.delete_dir(configuration.get_jpg_path())

        return same

    def interface(self, configurator: Config, plot: plt, tiers: Dict):
        """Draws image's size plot and captures the percent user value.

        :param Config configurator:
        :param plt plot:
        :param Dict tiers:
        :return:
        """

        # Drawing plot.
        print('Drawing plot...')
        plot.draw()
        plot.pause(0.001)

        print('Results:')
        for tier, count in tiers.items():
            print('* TIER {}%: {} images.'.format(tier, count))

        # User interaction.
        executing = True
        while executing:
            selected = -1
            while not (0 <= selected <= 100):
                try:
                    selected = int(input('> Enter a percent value (1 to 100) or enter 0 to finish: '))
                except ValueError:
                    print('Please, enter a NUMBER between 0 and 100')

            if selected != 0:
                result_dir = '{}{}/'.format(configurator.get_work_path(), FOLDER_NAME_OUTPUT_RESULT.format(selected))
                if not path.exists(result_dir):
                    self.get_result(configurator, selected)
                else:
                    print('Selected_{} already exist!'.format(selected))
            else:
                executing = False

    def get_result(self, configurator: Config, selected_percent: int):
        """ Copy the final selected images to `selected` folder.

        :param Config configurator:
        :param int selected_percent:
        :return:
        """
        result_dir = '{}{}/'.format(configurator.get_work_path(), FOLDER_NAME_OUTPUT_RESULT.format(selected_percent))
        self.create_dir(result_dir)

        print('Selecting between {} images with >= {}%...'.format(configurator.get_work_count(), selected_percent))
        for file in configurator.get_work_files():
            if file.get_jpg_percent() >= selected_percent:
                copyfile(file.get_path(), result_dir + file.get_name())
            else:
                break  # My list is sorted!

        print("DONE - Results with {}% in '{}'!".format(selected_percent, result_dir))

    @staticmethod
    def classifier_tiers(tiers: Dict, rank: float):
        for tier, val in tiers.items():
            if tier <= rank:
                tiers[tier] += 1

    @staticmethod
    def generate_plot(file_list: List[File]) -> plt:
        """ Creates Plot interface

        :param List[File] file_list:
        :return:
        """
        file_list.sort(key=lambda item: item.get_jpg_size(), reverse=True)
        interval = int(len(file_list) / 100)
        x, y = [], []

        i = 0
        for file in file_list:
            if i % interval == 0:
                y.append(file.get_jpg_percent())
                x.append(file.get_jpg_name())
            i += 1

        plt.plot(x, y)
        plt.tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False)
        plt.xlabel('Images')
        plt.ylabel('(%) Size')
        plt.gca().yaxis.grid(True)

        return plt

    @staticmethod
    def to_jpg(image_path: str, jpg_path: str):
        """Save an image to jpg.

        :param str image_path:
        :param str jpg_path:
        :return:
        """
        image = Image.open(image_path)
        image.save(jpg_path, IMAGE_FORMAT_JPEG)

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
            logging.error("Work Folder '{}' doesn't have any {} image!".format(configurator.get_work_path(),
                                                                               configurator.get_work_extension().upper()))
            return False

        return True