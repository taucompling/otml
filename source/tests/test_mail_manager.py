import unittest
from mail import MailManager

class TestMailManager(unittest.TestCase):
    def setUp(self):
        self.mail_manager = MailManager()

    def test_send_mail(self):
        log_segment = "Distance from target energy: 0 <br> number of bab's: 0"
        log_file_name = "chomsky_bb_demote_only.txt"
        self.mail_manager.send_mail(log_segment, log_file_name)


