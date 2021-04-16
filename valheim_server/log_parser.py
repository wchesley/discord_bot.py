import os
import re
import logging
import datetime

from datetime.parser import parse

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
            return self.message.replace(steam_connect_msg,'')
        elif zDOID_connect in self.message:
            # Death message: Got character ZDOID from Bytes : 0:0
            if self.message[:-1] == "0":
                pass #process death here: 
            full_message = self.message.replace(zDOID_connect,'')
            full_message = full_message.split(' ')
            return full_message[0]
        elif current_connections in self.message:
            connections = self.message.split(' ')
            # log message should look like: 'Connections 1 ZDOS:130588  sent:0 recv:422'
            return connections[1]
        elif disconnect in self.message:
            return self.message.replace(disconnect,'') # Should be steamID of player who disconnected

    def remove_text_inside_brackets(text, brackets="{}[]()"):
        """Helper function to remove brackets, and text within them, from string"""
        # Pulled from answer by jfs at https://stackoverflow.com/questions/14596884/remove-text-between-and/14603508#14603508
        # Count open/closed brackets
        count = [0] * (len(brackets) // 2)
        saved_chars = []
        for character in text: 
            for i,b in enumerate(brackets):
                if character == b: # Found a bracket!
                    kind, is_close = divmod(i,2)
                    count[kind] += (-1)**is_close # Where: '+1' is open and '-1' is closed
                    if count[kind] < 0: # unbalanced bracket (missing a close)
                        count[kind] =0 # keep the bad bracket
                    else: # Found good bracket, remove it!
                        break
                else: # Character is not a [balanced] bracket: 
                    if not any(count):
                        saved_chars.append(character)
        return ''.join(saved_chars)

    def remove_date(self, log_line):
        count = 0
        date = ''
        for char in log_line:
            if char == ':':
                count += 1
                date += char
            if count == 3:
                break
        logging.info(f'removing {date} from {log_line}')
        message = self.log_line.replace(date + ' ','')
        logging.info(f'message is now: {message}')
        # Remove trailing ':' from date: 
        new_date = date[:len(date) - 1]
        logging.info(f'Attempting to parse: {new_date}')
        try:
            date_object = datetime.strptime(new_date, '%m/%d/%Y %H:%M:%S')
            logging.info(f'parsed date: {date_object}')
            return date_object, message
        except (ValueError, TypeError):
            logging.error(f'Failed to parse date')
            return new_date, message

    def extract_prefix_from_string(self):
        """ Remove prefix from Vlaheim Plus server logs, returns Date as datetime obj and the log message as string\n 
        Removes anything within [brackets], example: [Info : Unity Log] """
        prefix = ''
        for char in self.log_line:
            if char == '[':
                prefix += char
            if char == ']':
                prefix += char
                break
        logging.info(f'prefix is: {prefix}')
        message = self.log_line.replace(prefix + ' ', '')
        date, message = self.remove_date(message)
        logging.info(f'Returning: {date}\n{message}')
        return date, message