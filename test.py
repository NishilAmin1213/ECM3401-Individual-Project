import unittest

from ves import _get_details_VES, query_VES
from plate_processor import *

class TestVES(unittest.TestCase):

    def test_get_details_VES(self):
        res = _get_details_VES('AA19AAA')
        if res == None:
            unittest.TestCase().fail("None returned from _get_details_VES")
        self.assertEqual(res['registrationNumber'], 'AA19AAA', 'the registration Number key was not in the return dictionary, therefore the request must have been unsuccessful')

    def test_query_VES(self):
        res = query_VES('AA19AAA')
        if not res['ves_found']:
            unittest.TestCase().fail("'ves_found' is 'False' - 'AA19AAA' should return True")
