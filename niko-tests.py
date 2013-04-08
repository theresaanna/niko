from flask.ext.testing import TestCase
import datetime
import unittest
import niko

class TestDates(unittest.TestCase):

  def setUp(self):
    self.test_datetime = datetime.datetime(2013, 4, 8, 19, 49, 5, 707949)  

  def test_date_to_timestamp(self):
    self.assertEqual(1365450545, niko.get_unix_timestamp(self.test_datetime))

if __name__ == '__main__':
  unittest.main()
