import os
import re
import logging
import datetime
import datefinder

from datetime import datetime


class LogLine:
    def __init__(self, log_line):
        self.log_line = log_line
        #self.date, self.message = self.remove_date()

    def remove_text_inside_brackets(text, brackets="{}[]()"):
        """Helper function to remove brackets, and text within them, from string"""
        # Pulled from answer by jfs at https://stackoverflow.com/questions/14596884/remove-text-between-and/14603508#14603508
        # Count open/closed brackets
        count = [0] * (len(brackets) // 2)  # count open/close brackets
        saved_chars = []
        for character in text:
            for i, b in enumerate(brackets):
                if character == b:  # found bracket
                    kind, is_close = divmod(i, 2)
                    count[kind] += (-1)**is_close  # `+1`: open, `-1`: close
                    if count[kind] < 0:  # unbalanced bracket
                        count[kind] = 0  # keep it
                    else:  # found bracket to remove
                        break
            else:  # character is not a [balanced] bracket
                if not any(count):  # outside brackets
                    saved_chars.append(character)
        # Rejoin the characters into a string: 
        message = ''.join(saved_chars)
        print(f'Messsage before strip: {message}')
        # Remove any trailing or leading whitespace
        message = message.strip()
        print(f'returning: {message}')
        return message

    def remove_date(log_line):
        """ Remove date from valheim server log message, retuns message and date as datetime object."""
        # Incoming format has to be: 04/12/2021 19:55:55: Closing socket 76561197999876368
        new_date = datefinder.find_dates(log_line)
        if new_date != None or 0 or "":
            print("No date found, returning...")
            return 1, 1
        else:
            print(f'Received: {log_line}')

            logging.info(f'removing {new_date} from {log_line}')
            message = log_line.replace(new_date + ':', '').strip()
            print(f'message is now: {message}')
            return new_date, message
