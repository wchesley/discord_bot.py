## TODO: 
# set log file location (Config.json?)
# Read file up to present
# Read any new lines written to file
# Pass information from within log files to log_parser.py
# avoid duplicates? 

import os
import discord
import logging
import time
from utils import default

SLEEP_SECONDS = 1

class ValheimLogDog:

    def __init__(self):
        self.config = default.config()

    def start(self):
        logging.debug(f"Fetching log file at: {self.config['log_file']}")
        with open(self.config['log_file'], 'r') as log_file:
            logging.debug(f'opened context for log file at: {log_file}')
            for new_lines in self.line_watcher(log_file):
                logging.debug(f'Processing the lines found...')
                new_lines = self.filter_lines(new_lines)
                logging.debug(f'\t> Processed lines: {new_lines}')

                for line in new_lines:
                    #parse lines read here: 

    def line_watcher(self, file):
        """Generator function that returns the new line entered."""

        file.seek(0, os.SEEK_END)

        while True:
            # Reads last line
            new_lines = file.readlines()
            # sleep if file hasn't been updated
            if not new_lines:
                logging.debug(f'No new lines. Sleeping {SLEEP_SECONDS}')
                time.sleep(SLEEP_SECONDS)
                continue
            logging.debug('New line(s) found!')

            for l in new_lines:
                logging.debug('\t> {}'.format(l.replace('\n', '')))

            yield new_lines
    
    def filter_lines(self, lines):
        """Filters the log lines to only return the ones that have actual values."""
        return [l for l in lines if l != '\n' and len(l) > 1]