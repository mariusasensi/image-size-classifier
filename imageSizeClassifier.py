import sys
import argparse
import logging
from src.Config import Config
from src.Service import Service
from src.Constants import ACCEPTED_IMAGE_FORMATS, LOGGING_LEVELS


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
    service = Service()
    service.execute(Config(arguments.path, arguments.extension, arguments.keep))
    print(' - DONE - ')
    exit(0)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(' - INTERRUPTED - ')
        sys.exit(1)
