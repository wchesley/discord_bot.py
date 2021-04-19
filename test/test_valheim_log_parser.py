import unittest
from unittest import TestResult
from valheim_server.log_parser import LogLine
from valheim_server.log_dog import ValheimLogDog

from datetime import datetime

class TestValheimLogParser(unittest.TestCase):
    def setUp(self):
        self.log_line = '[Info   : Unity Log] 04/12/2021 19:55:55: Closing socket 76561197999876368'
        self.test_log_message_Steam = 'Got connection SteamID 76561197999876368'
        self.test_log_date_Steam = "04/12/2021 19:35:20"
        self.test_log_message_zDOID = '[Info   : Unity Log] 04/12/2021 19:35:55: Got character ZDOID from Halfdan : 3267341458:1'
        self.test_log_message_char_death = '[Info   : Unity Log] 04/12/2021 19:55:55: Got character ZDOID from Bytes : 0:0'


    def test_remove_test_inside_brackets(self):
        message_without_prefix = LogLine.remove_text_inside_brackets(self.log_line)
        self.assertEqual(message_without_prefix, '04/12/2021 19:55:55: Closing socket 76561197999876368')
    
   

    def test_remove_date(self):
        # remove_date method expects no prefix!
        message_without_prefix = LogLine.remove_text_inside_brackets(self.log_line)
        date, message = LogLine.remove_date(message_without_prefix)
        self.assertEqual(date, datetime(2021, 4, 12, 19, 55, 55))
        self.assertEqual(message, 'Closing socket 76561197999876368')

   

    def zDOIDFromValheimLogMessage(self):
        pass

    def CharacterDeathFromValheimLogMessage(self):
        pass

# def suite():
#     suite = unittest.TestSuite()
#     suite.addTest(unittest.makeSuite(TestValheimLogParser))
#     return suite
# if __name__ == '__main__':
#     runner = unittest.TextTestRunner()
#     test_suite = TestValheimLogParser.Suite()
#     result = runner.run(test_suite)
#     print ("---- START OF TEST RESULTS")
#     print (result)

#     print ("result::errors")
#     print (result.errors)

#     print ("result::failures")
#     print (result.failures)

#     print ("result::skipped")
#     print (result.skipped)

#     print ("result::successful")
#     print (result.wasSuccessful())

#     print ("result::test-run")
#     print (result.testsRun)
#     print ("---- END OF TEST RESULTS")