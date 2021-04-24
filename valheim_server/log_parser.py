import os
import re
import logging
import datetime

from datetime import datetime
from utils import default


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
        default.s_print(f'Messsage before strip: {message}')
        # Remove any trailing or leading whitespace
        message = message.strip()
        default.s_print(f'returning: {message}')
        return message

    def remove_date(log_line):
        """ Remove date from valheim server log message, retuns message and date as datetime object."""
        # Incoming format has to be: 04/12/2021 19:55:55: Closing socket 76561197999876368
        #log_line = log_line.strip() # Remove leading and trailing whitespace: 
        default.s_print(f'Received: \n{log_line}\n^^^ REMOVE_DATE()')
        new_date = LogLine.strip_date_from_string(log_line)
        message = log_line.replace(str(new_date) + ': ','')
        default.s_print(f'New date type: {type(new_date)}\nData: {new_date}\nMessage type: {type(message)}\nData: {message}')
        return new_date, message


    def strip_date_from_string(date, removal_char=':'):
        count = 0
        #removal_char = ':'
        date_chars = ''
        for char in date:
            if char == removal_char:
                count += 1
            if count == 3:
                break
            date_chars += char
        date_string = "".join(date_chars)
        # try:
        #     date_string = datetime.strptime(date_string, "%m/%d/%Y %H:%M:%S")
        #     return date_string
        # except ValueError as e:
        #     default.s_print(f"error parsing date: {e}")
        default.s_print(f'strip date from string: {date_string}')
        return date_string
