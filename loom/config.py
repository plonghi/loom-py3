import ConfigParser
import os
import sys
import logging
import pdb

from math import pi
from sympy import oo

class LoomConfigParser(ConfigParser.SafeConfigParser):
    """
    A wrapper of SafeConfigParser.
    """

    def get(self, section, option):
        """
        Returns a value of an option as a Python expression,
        whereas ConfigParser.get() returns a value as a string.
        """
        value = ConfigParser.SafeConfigParser.get(self, section, option)
        return eval(value)

    def getstr(self, section, option):
        """
        Returns a value as a string.
        """
        return ConfigParser.SafeConfigParser.get(self, section, option)


class LoomConfig:
    """
    A container class of the configuration data.
    Saves the configuration data as a Python dictionary.
    """
    def __init__(self, logger_name='loom_logger'):
        self.data = {}
        self.parser = None
        self.logger_name = logger_name


    def __setitem__(self, option, value):
        self.data[option] = value


    def __getitem__(self, option):
        logger = logging.getLogger(self.logger_name)
        try:
            value = self.data[option]
        except KeyError as e:
            logger.warning('Option {} not specified; use None.'.format(e))
            #self.data[option] = None
            value = None
        return value

    def keys(self):
        return self.data.keys()

    def iteritems(self):
        return self.data.iteritems()


    def read(self, config_file):
        """
        Read an .ini file and load the configuration data.
        """
        config_parser = LoomConfigParser()

        with open(config_file, 'r') as fp:
            config_parser.readfp(fp)

        for section in config_parser.sections():
            for option in config_parser.options(section):
                if (section == 'Seiberg-Witten data'):
                    self[option] = config_parser.getstr(section, option)
                else:
                    self[option] = config_parser.get(section, option)

        self.parser = config_parser
