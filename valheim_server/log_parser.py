import os
import re
import logging
import datetime

from datetime import datetime


class LogLine:
    def __init__(self, log_line):
        self.log_line = log_line
        self.date, self.message = self.extract_prefix_from_string()

    def extract_log_parts(self):
        """Get the goods from the valheim log message"""
        # Trailing space on the end is intentional, needed to remove that part of the log message
        steam_connect_msg = 'Got connection SteamID '
        zDOID_connect = 'Got character ZDOID from '
        current_connections = ['Connections', 'ZDOS:']
        disconnect = "Closing Socket "
        if steam_connect_msg in self.message:
            self.data['SteamID'] = self.message.replace(steam_connect_msg, '')
            return self.message.replace(steam_connect_msg, '')
        elif zDOID_connect in self.message:
            # Death message: Got character ZDOID from Bytes : 0:0
            if self.message[:-1] == "0":
                pass  # process death here:
            full_message = self.message.replace(zDOID_connect, '')
            full_message = full_message.split(' ')
            return full_message[0]
        elif current_connections in self.message:
            connections = self.message.split(' ')
            # log message should look like: 'Connections 1 ZDOS:130588  sent:0 recv:422'
            return connections[1]
        elif disconnect in self.message:
            # Should be steamID of player who disconnected
            return self.message.replace(disconnect, '')

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
        # Remove any trailing or leading whitespace
        message = message.strip()
        return message

    def remove_date(log_line):
        """ Remove date from valheim server log message, retuns message and date as datetime object."""
        # Incoming format has to be: 04/12/2021 19:55:55: Closing socket 76561197999876368
        # Call remove_text_inside_brackets() to remove the bracket prefix first!
        if log_line[0] == '[':
            print(f'bad input removing prefix: {log_line}')
            log_line = LogLine.remove_date(log_line)
        split = log_line.split(' ',2)
        for s in split:
            print(f'Split: {s}')
        # after split, first and second index has the date plus trailing ':'
        date = split[0] +' ' + split[1]
        logging.info(f'removing {date} from {log_line}')
        message = log_line.replace(date + ' ', '').strip()
        print(f'message is now: {message}')
        # Remove trailing ':' from date:
        new_date = date[:len(date) - 1]
        logging.info(f'Attempting to parse: {new_date}')
        try:
            date_object = datetime.strptime(new_date, '%m/%d/%Y %H:%M:%S')
            print(f'parsed date: {date_object}')
            return date_object, message
        except (ValueError, TypeError):
            print(f'Failed to parse date')
            return new_date, message
