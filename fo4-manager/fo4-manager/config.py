import sys
from configparser import ConfigParser

import logging
err_logger = logging.getLogger('error_logger')

class Data:
    def __init__(self):
        self.__file = None
        self.__login_details = dict()
        try:
            self.__file = open('cfg/data.txt', 'r')
        except OSError:
            err_logger.error("Cannot open the data file.")
            sys.exit("An error has occurred, see the '{}' file.".format(err_logger.handlers[0].baseFilename))
        else:
            self.parse()

    def __del__(self):
        if self.__file is not None: 
            self.__file.close()

    def parse(self):
        self.__login_details.clear() 
        for line in self.__file.read().splitlines():
            if line:
                try:
                    elements = line.split(':', 1)
                    self.__login_details[elements[0]] = elements[1]
                except (ValueError, IndexError):
                    continue

    @property
    def get(self):
        return self.__login_details

class Settings:
    def __init__(self):
        self.__file = None
        self.__settings = ConfigParser()
        try:
            self.__file = open('cfg/settings.ini', 'r')
        except OSError:
            err_logger.error("Cannot open the settings file.")
            sys.exit("An error has occurred, see the '{}' file.".format(err_logger.handlers[0].baseFilename))
        else:
            self.parse()

    def __del__(self):
        if self.__file is not None: 
            self.__file.close()

    def parse(self):
        self.__settings.read_file(self.__file)

    @property
    def get(self):
        return self.__settings