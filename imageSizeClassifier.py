import sys
import argparse
import logging
from src.Config import Config
from src.SizeClassifierService import SizeClassifierService
from src.NoiseReductionService import NoiseReductionService
from src.Constants import ACCEPTED_IMAGE_FORMATS, LOGGING_LEVELS


def menu(configurator: Config):
    print(' -- MENU --')
    print('1 -> Image Size Classifier')
    print('2 -> Image Noise Reduction Classifier')

    # User interaction.
    executing = True
    while executing:
        selected = -1
        while not (0 <= selected <= 2):
            try:
                selected = int(input('> Enter a option or enter 0 to finish: '))
            except ValueError:
                print('Please, enter a NUMBER between 0 and 2')

        if selected == 1:
            size_classifier_service = SizeClassifierService()
            size_classifier_service.execute(configurator)
            executing = False
        elif selected == 2:
            noise_reduction_service = NoiseReductionService()
            noise_reduction_service.execute(configurator)
            executing = False
        else:
            executing = False

    print(' - DONE - ')


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

    configurator = Config(arguments.path, arguments.extension, arguments.keep)
    menu(configurator)
    exit(0)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(' - INTERRUPTED - ')
        sys.exit(1)
