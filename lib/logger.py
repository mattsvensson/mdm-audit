#!/usr/bin/env python3
from lib.constants import *
from lib.arg_parser import *
import logging
from logging.handlers import RotatingFileHandler
import os
from termcolor import colored


class MyFormatter(logging.Formatter):
    """
        Custom Formatter with colored [*], based on criticality, instead of words
    """
    def format(self, record):
        #Make the custom level marker
        record.levelname = record.levelname.replace(
                                                    "CRITICAL",colored("[*]","red", attrs=['bold'])
                                                   ).replace(
                                                    "ERROR",colored("[*]","red", attrs=['bold'])
                                                   ).replace(
                                                    "WARNING",colored("[*]","yellow", attrs=['bold'])
                                                   ).replace(
                                                    "INFO",colored("[*]","green", attrs=['bold'])
                                                   ).replace(
                                                    "DEBUG",colored("[*]","green", attrs=['bold'])
                                                   )
        
        #Make the newline start before the level if there is one in the message
        if record.msg.startswith("\n"):
            record.level_label = "\n%s" % (record.levelname)
        else:
            record.level_label = "%s" % (record.levelname)

        #Be sure message is stripped either way
        record.message_text = record.msg.strip()

        #Return the newly formatted record
        return logging.Formatter.format(self, record)


class Logger():
    def __init__(self, print_verbose, print_very_verbose):
        self.log = logging.getLogger()

        #Add command line handliner
        ch = logging.StreamHandler()
        #Set the level
        if print_very_verbose:
            self.log.setLevel(logging.DEBUG)
        elif print_verbose:
            self.log.setLevel(logging.INFO)
        else:
            self.log.setLevel(logging.WARNING)
        #Custom format for printing to the screen
        formatter_stdout = MyFormatter('''{level_label} {message_text}'''.format(
            level_label='%(level_label)s', 
            message_text='%(message_text)s'.strip()
        ))
        ch.setFormatter(formatter_stdout)
        self.log.addHandler(ch)

        # Set logging for requests to warning
        logging.getLogger("requests").setLevel(logging.WARNING)
        logging.getLogger("urllib3").setLevel(logging.WARNING)

#Create the logger
logger = Logger(print_verbose=args.print_verbose, print_very_verbose=args.print_very_verbose)
