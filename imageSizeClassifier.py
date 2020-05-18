from os import makedirs, path
from sys import exit
import argparse
import logging
from shutil import rmtree, copyfile
import glob
from PIL import Image
import matplotlib.pyplot as plt
from typing import List, Dict

# Folders.
FOLDER_NAME_OUTPUT_JPG = 'jpg'
FOLDER_NAME_OUTPUT_RESULT = 'selected_{}'

# Formats.
IMAGE_FORMAT_TIF = 'TIF'
IMAGE_FORMAT_TIFF = 'TIFF'
IMAGE_FORMAT_BMP = 'BMP'
IMAGE_FORMAT_PNG = 'PNG'
IMAGE_FORMAT_JPEG = 'JPEG'
IMAGE_FORMAT_JPG = 'JPG'

# Tiers.
IMAGE_INTERVAL_TIERS = 10

# Lists.
ACCEPTED_IMAGE_FORMATS = [IMAGE_FORMAT_TIF, IMAGE_FORMAT_TIFF, IMAGE_FORMAT_BMP, IMAGE_FORMAT_PNG]
LOGGING_LEVELS = [logging.ERROR, logging.WARNING, logging.INFO, logging.DEBUG]
PERCENT_TIERS = dict((i, 0) for i in range(0, 100, IMAGE_INTERVAL_TIERS))


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


def create_dir(directory: str):
    makedirs(directory)


def delete_dir(directory: str):
    rmtree(directory)


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


def is_already_worked(configuration: Config) -> bool:
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
        delete_dir(configuration.get_jpg_path())

    return same


def execute(configurator: Config):
    """Core

    :param Config configurator:
    :return:
    """
    if not is_valid_config(configurator):
        exit(1)

    print("Work folder: '{}'.".format(configurator.get_work_path()))
    print("Found {} {} images.".format(configurator.get_work_count(), configurator.get_work_extension().upper()))
    print("JPG folder: '{}'.".format(configurator.get_jpg_path()))

    if not is_already_worked(configurator):
        create_dir(path.dirname(configurator.get_jpg_path()))
        iter_max = configurator.get_work_count()
        counter = 1

        print('[START] Conversion {} to {}.'.format(configurator.get_work_extension().upper(), IMAGE_FORMAT_JPG))
        for work_file in configurator.get_work_files():
            jpg_path = '{}{}.{}'.format(configurator.get_jpg_path(), work_file.get_name(), IMAGE_FORMAT_JPG.lower())
            print("[{}/{}] Converting: '{}' -> '{}'".format(counter, iter_max, work_file.get_path(), jpg_path))
            to_jpg(work_file.get_path(), jpg_path)
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

    tiers = PERCENT_TIERS
    for file in configurator.get_work_files():
        image_percent = round(((file.get_jpg_size() - minimum) * 100 / (maximum - minimum)), 4)
        file.set_jpg_percent(image_percent)
        classifier_tiers(tiers, image_percent)

    plot = generate_plot(configurator.get_work_files())
    interface(configurator, plot, tiers)

    if not configurator.keep_results():
        print("Deleting '{}' path...".format(configurator.get_jpg_path()))
        delete_dir(configurator.get_jpg_path())
    else:
        print("Folder '{}' hasn't been deleted because it has been decided to keep it for future runs.".format(
            configurator.get_jpg_path()))


def classifier_tiers(tiers: Dict, rank: float):
    for tier, val in tiers.items():
        if tier <= rank:
            tiers[tier] += 1


def interface(configurator: Config, plot: plt, tiers: Dict):
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
                get_result(configurator, selected)
            else:
                print('Selected_{} already exist!'.format(selected))
        else:
            executing = False


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


def get_result(configurator: Config, selected_percent: int):
    """ Copy the final selected images to `selected` folder.

    :param Config configurator:
    :param int selected_percent:
    :return:
    """
    result_dir = '{}{}/'.format(configurator.get_work_path(), FOLDER_NAME_OUTPUT_RESULT.format(selected_percent))
    create_dir(result_dir)

    print('Selecting between {} images with >= {}%...'.format(configurator.get_work_count(), selected_percent))
    for file in configurator.get_work_files():
        if file.get_jpg_percent() >= selected_percent:
            copyfile(file.get_path(), result_dir + file.get_name())
        else:
            break  # My list is sorted!

    print("DONE - Results with {}% in '{}'!".format(selected_percent, result_dir))


def to_jpg(image_path: str, jpg_path: str):
    """Save an image to jpg.

    :param str image_path:
    :param str jpg_path:
    :return:
    """
    image = Image.open(image_path)
    image.save(jpg_path, IMAGE_FORMAT_JPEG)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', action='count', default=0,
                        help='Indicates the level of messages to be displayed.')
    parser.add_argument('-k', '--keep', const=str, action='store_const', default=False,
                        help='Keeps the temporary files for future runs.')
    parser.add_argument('--path', required=True,
                        help='REQUIRED: Path with all images to work.')
    parser.add_argument('--extension', required=True, choices=[ext.lower() for ext in ACCEPTED_IMAGE_FORMATS],
                        help='REQUIRED: Images extension')
    arguments = parser.parse_args()

    logging.basicConfig(level=LOGGING_LEVELS[min(len(LOGGING_LEVELS) - 1, arguments.verbose)],
                        format='[%(levelname)s] %(message)s')

    print(' - IMAGE SIZE CLASSIFIER - ')
    execute(Config(arguments.path, arguments.extension, arguments.keep))
    print(' - DONE - ')
    exit(0)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(' - INTERRUPTED - ')
        exit(1)
