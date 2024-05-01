import unittest
from unittest.mock import patch, MagicMock
from plate_processor import _perform_adjustments, _validate_plate, _generate_plate_variants, _filter_all_guesses, _find_missing_chars
from ves import query_VES

class TestPlateProcessor(unittest.TestCase):

    def test_perform_adjustments(self):
        # Test the _perform_adjustments function
        # Test if the area code has a misread character
        # Test if a 1 read in as an I is replaced with a 1
        input = 'AAI9AAA'
        expected_output = 'AA19AAA'
        self.assertEqual(_perform_adjustments(input), expected_output)

    def test_perform_adjustments_1(self):
        # Test the _perform_adjustments function
        # Test if the year has a misread character
        # Test if a O read in as an 0 is replaced with a O
        input = 'A019AAA'
        expected_output = 'AO19AAA'
        self.assertEqual(_perform_adjustments(input), expected_output)

    def test_perform_adjustments_2(self):
        # Test the _perform_adjustments function
        # Test if the final 3 characters has a misread character
        # Test if a O read in as an 0 is replaced with a O
        input = 'AA19A0A'
        expected_output = 'AA19AOA'
        self.assertEqual(_perform_adjustments(input), expected_output)

    def test_perform_adjustments_3(self):
        # Test the _perform_adjustments function
        # Test if no adjustments are needed
        # AA19AAA does not need any adjustments
        input = 'AA19AAA'
        expected_output = 'AA19AAA'
        self.assertEqual(_perform_adjustments(input), expected_output)

    def test_perform_adjustments_4(self):
        # Test the _perform_adjustments function
        # Test if multiple adjustments are needed
        # A0I9A0A needs multiple adjustments, characters 2, 4 and 6 need to be changed
        input = 'A0I9A0A'
        expected_output = 'AO19AOA'
        self.assertEqual(_perform_adjustments(input), expected_output)

    def test_perform_adjustments_5(self):
        # Test the _perform_adjustments function
        # Test if the input is empty
        input = ''
        expected_output = ''
        self.assertEqual(_perform_adjustments(input), expected_output)

    def test_validate_plate(self):
        # Test the _validate_plate function
        # Test if the year is invalid
        # 49 is not a valid year as it cannot start with a 4
        input = 'AA49AAA'
        self.assertFalse(_validate_plate(input))

    def test_validate_plate_1(self):
        # Test the _validate_plate function
        # Test if the year is invalid
        # A9 is not a valid year as it should contain 2 numbers, no letters
        input = 'AAA9AAA'
        self.assertFalse(_validate_plate(input))

    def test_validate_plate_2(self):
        # Test the _validate_plate function
        # Test if the area code is invalid
        # A9 is not a valid area code as it should contain 2 letters, no numbers
        input = 'A919AAA'
        self.assertFalse(_validate_plate(input))

    def test_validate_plate_3(self):
        # Test the _validate_plate function
        # Test if the length is invalid
        # A19AAA is not a valid length as it should contain 7 characters
        input = 'A19AAA'
        self.assertFalse(_validate_plate(input))

    def test_validate_plate_4(self):
        # Test the _validate_plate function
        # Test if the length is invalid
        # AA19AAAA is not a valid length as it should contain 7 characters
        input = 'AA19AAAA'
        self.assertFalse(_validate_plate(input))

    def test_validate_plate_5(self):
        # Test the _validate_plate function
        # Test if the final three characters are invalid
        # AA199AA is not a valid final three characters as it should contain 3 letters, not numbers
        input = 'AA199AA'
        self.assertFalse(_validate_plate(input))

    def test_validate_plate_6(self):
        # Test the _validate_plate function
        # Test if the plate is correct
        # AA19AAA is a valid plate
        input = 'AA19AAA'
        self.assertTrue(_validate_plate(input))

    def test_validate_plate_7(self):
        # Test the _validate_plate function
        # Test if the plate contains special characters
        # AA19A*A is not a valid palte as it contains a *
        input = 'AA19A*A'
        self.assertFalse(_validate_plate(input))

    def test_validate_plate_8(self):
        # Test the _validate_plate function
        # Test if the plate contains lower case letters
        # AA19AAA is not a valid plate as it contains lower case letters
        input = 'aa19AAA'
        self.assertFalse(_validate_plate(input))

    def test_validate_plate_9(self):
        # Test the _validate_plate function
        # Test if the plate is empty
        # An empty string is not a valid plate
        input = ''
        self.assertFalse(_validate_plate(input))

    def test_validate_plate_10(self):
        # Test the _validate_plate function
        # Test if the plate contains white spaces
        # AA19 AA is not a valid plate as it contains white spaces
        input = 'AA19 AA'
        self.assertFalse(_validate_plate(input))

    def test_query_VES(self):
        # Test the query_VES function
        input = 'AA19AAA'
        result = query_VES(input)

        # Assert that the returned dictionary has the correct keys
        self.assertIn('ves_found', result)
        self.assertIn('reg_no', result)
        self.assertIn('ves_make', result)
        self.assertIn('ves_color', result)
        self.assertIn('ves_mot', result)
        self.assertIn('ves_tax', result)

        # Assert that the returned values match the expected values
        self.assertEqual(result['ves_found'], True)
        self.assertEqual(result['reg_no'], 'AA19AAA')
        self.assertEqual(result['ves_make'], 'Mercedes-Benz')
        self.assertEqual(result['ves_color'], 'White')
        self.assertEqual(result['ves_mot'], 'Valid')
        self.assertEqual(result['ves_tax'], 'Taxed')

    def test_query_VES_1(self):
        # Test the query_VES function with a non-existent (or invalid) number plate
        input = 'ZZ99ZZZ'
        result = query_VES(input)

        # Assert that the returned dictionary has the correct keys
        self.assertIn('ves_found', result)

        # Assert that the 'ves_found' value is False
        self.assertEqual(result['ves_found'], False)

    def test_query_VES_2(self):
        # Test the query_VES function
        input = 'AA19AAA'
        result = query_VES(input)

        # Assert that the returned dictionary has the correct keys
        self.assertIn('ves_found', result)
        self.assertIn('reg_no', result)
        self.assertIn('ves_make', result)
        self.assertIn('ves_color', result)
        self.assertIn('ves_mot', result)
        self.assertIn('ves_tax', result)

        # Assert that the returned values match the expected values
        self.assertEqual(result['ves_found'], True)
        self.assertEqual(result['reg_no'], 'AA19AAA')
        self.assertNotEqual(result['ves_make'], 'BMW')
        self.assertNotEqual(result['ves_color'], 'Black')



    def test_generate_plate_variants(self):
        input_plate = 'AA19AAA'
        expected_output = set(['AA19AAN', 'BA19AAA', 'AA13AAA', 'AA19AUA', 'AA19AAU', 'AA19NAA', 'AA19AFA', 'AA19FAA', 'XA19AAA', 'AA19AYA', 'KA19AAA', 'AA19AOA', 'AA15AAA', 'AA18AAA', 'AC19AAA', 'YA19AAA', 'AA19AAO', 'AR19AAA', 'AA19ACA', 'UA19AAA', 'AF19AAA', 'AA19AAV', 'AA19DAA', 'AA19OAA', 'AA19BAA', 'AA19ABA', 'AA19GAA', 'JA19AAA', 'AA19AWA', 'AA19XAA', 'AA19ATA', 'AA09AAA', 'AA19VAA', 'AA79AAA', 'VA19AAA', 'AX19AAA', 'CA19AAA', 'HA19AAA', 'AJ19AAA', 'AA19AXA', 'AA19TAA', 'SA19AAA', 'AA19AAS', 'AA19RAA', 'FA19AAA', 'AA16AAA', 'AA19WAA', 'AA19AAG', 'DA19AAA', 'AA19AAA', 'AA19PAA', 'AA19AAB', 'AM19AAA', 'AA19AAF', 'AA19ASA', 'AA19AAM', 'AA19AGA', 'AA19LAA', 'AA19AAP', 'AB19AAA', 'AA19UAA', 'LA19AAA', 'AA17AAA', 'AA19EAA', 'TA19AAA', 'GA19AAA', 'AA19AMA', 'AA19AAL', 'AY19AAA', 'AA59AAA', 'AA19ANA', 'AA19AKA', 'AA19ADA', 'AA19CAA', 'AA19YAA', 'RA19AAA', 'AH19AAA', 'AA19AAD', 'AA19AJA', 'AV19AAA', 'AA19HAA', 'AA19AAC', 'AE19AAA', 'AA19KAA', 'PA19AAA', 'AA19AAH', 'AD19AAA', 'AL19AAA', 'AU19AAA', 'AA19AAE', 'AA19AAJ', 'AS19AAA', 'AN19AAA', 'AA19JAA', 'AK19AAA', 'NA19AAA', 'AA19ZAA', 'AA69AAA', 'AA19AHA', 'EA19AAA', 'AA11AAA', 'AA19SAA', 'AA19AVA', 'MA19AAA', 'AA19AAW', 'AA19AAX', 'AA19APA', 'AA19ARA', 'AW19AAA', 'AA19ALA', 'AA19AAK', 'AA12AAA', 'AA19MAA', 'WA19AAA', 'AG19AAA', 'AA19AAZ', 'AP19AAA', 'AA19AAY', 'AA14AAA', 'AA10AAA', 'AA29AAA', 'AA19AZA', 'AT19AAA', 'AA19AAT', 'AA19AEA', 'AA19AAR'])
        self.assertEqual(set(_generate_plate_variants(input_plate)), expected_output)

    def test_filter_all_guesses(self):
        # Test the _filter_all_guesses function
        input = ['AA19AAN', 'BA19AAA', 'AA13AAA', 'AA19AUA', 'AA19AAU', 'AA19NAA', 'AA19AFA', 'AA19FAA', 'XA19AAA', 'AA19AYA', 'KA19AAA', 'AA19AOA', 'AA15AAA', 'AA18AAA', 'AC19AAA', 'YA19AAA', 'AA19AAO', 'AR19AAA', 'AA19ACA', 'UA19AAA', 'AF19AAA', 'AA19AAV', 'AA19DAA', 'AA19OAA', 'AA19BAA', 'AA19ABA', 'AA19GAA', 'JA19AAA', 'AA19AWA', 'AA19XAA', 'AA19ATA', 'AA09AAA', 'AA19VAA', 'AA79AAA', 'VA19AAA', 'AX19AAA', 'CA19AAA', 'HA19AAA', 'AJ19AAA', 'AA19AXA', 'AA19TAA', 'SA19AAA', 'AA19AAS', 'AA19RAA', 'FA19AAA', 'AA16AAA', 'AA19WAA', 'AA19AAG', 'DA19AAA', 'AA19AAA', 'AA19PAA', 'AA19AAB', 'AM19AAA', 'AA19AAF', 'AA19ASA', 'AA19AAM', 'AA19AGA', 'AA19LAA', 'AA19AAP', 'AB19AAA', 'AA19UAA', 'LA19AAA', 'AA17AAA', 'AA19EAA', 'TA19AAA', 'GA19AAA', 'AA19AMA', 'AA19AAL', 'AY19AAA', 'AA59AAA', 'AA19ANA', 'AA19AKA', 'AA19ADA', 'AA19CAA', 'AA19YAA', 'RA19AAA', 'AH19AAA', 'AA19AAD', 'AA19AJA', 'AV19AAA', 'AA19HAA', 'AA19AAC', 'AE19AAA', 'AA19KAA', 'PA19AAA', 'AA19AAH', 'AD19AAA', 'AL19AAA', 'AU19AAA', 'AA19AAE', 'AA19AAJ', 'AS19AAA', 'AN19AAA', 'AA19JAA', 'AK19AAA', 'NA19AAA', 'AA19ZAA', 'AA69AAA', 'AA19AHA', 'EA19AAA', 'AA11AAA', 'AA19SAA', 'AA19AVA', 'MA19AAA', 'AA19AAW', 'AA19AAX', 'AA19APA', 'AA19ARA', 'AW19AAA', 'AA19ALA', 'AA19AAK', 'AA12AAA', 'AA19MAA', 'WA19AAA', 'AG19AAA', 'AA19AAZ', 'AP19AAA', 'AA19AAY', 'AA14AAA', 'AA10AAA', 'AA29AAA', 'AA19AZA', 'AT19AAA', 'AA19AAT', 'AA19AEA', 'AA19AAR']
        expected_output = ['AA19AAA']
        predicted_color = 'White'
        predicted_make = 'Mercedes-Benz'
        self.assertEqual(_filter_all_guesses(predicted_color, predicted_make, input), expected_output)

    def test_filter_all_guesses_1(self):
        # Test the _filter_all_guesses function
        input_guesses = ['BB19BBB', 'CC19CCC', 'DD19DDD']
        predicted_color = 'White'
        predicted_make = 'Mercedes-Benz'
        expected_output = []
        self.assertEqual(_filter_all_guesses(predicted_color, predicted_make, input_guesses), expected_output)

    def test_find_missing_chars(self):
        # Test the _find_missing_chars function
        # Test if the input is a valid plate
        # AA19AAA is a valid plate, so it should return the plate itself
        input = 'AA19AAA'
        expected_output = (1, {'AA19AAA'})
        self.assertEqual(_find_missing_chars(input), expected_output)

    def test_find_missing_chars_1(self):
        # Test the _find_missing_chars function
        # Test if the input is an invalid plate
        # AA19AA is an invalid plate as it is missing one character
        input = 'AA19AA'
        expected_output = (70, {'AA19OAA', 'AA19ABA', 'AA19AAZ', 'AA19AAK', 'AA19AAC', 'AA19AYA', 'AA19AAT', 'AA19FAA', 'AA19AAP', 'AA19AAE', 'AA19APA', 'AA19RAA', 'AA19AAY', 'AA19NAA', 'AA19PAA', 'AA19UAA', 'AA19AOA', 'AA19AAL', 'AA19ACA', 'AA19CAA', 'AA19LAA', 'AA19AFA', 'AA19VAA', 'AA19AAM', 'AA19ANA', 'AA19AAG', 'AA19AMA', 'AA19AAA', 'AA19AAS', 'AA19ADA', 'AA19AAH', 'AA19AAD', 'AA19HAA', 'AA19AHA', 'AA19AXA', 'AA19JAA', 'AA19AKA', 'AA19KAA', 'AA19ASA', 'AA19AAV', 'AA19YAA', 'AA19ARA', 'AA19AAX', 'AA19AEA', 'AA19AAN', 'AA19AVA', 'AA19AWA', 'AA19AAB', 'AA19DAA', 'AA19SAA', 'AA19EAA', 'AA19AAU', 'AA19AAO', 'AA19AAF', 'AA19XAA', 'AA19AZA', 'AA19WAA', 'AA19TAA', 'AA19AAW', 'AA19AAJ', 'AA19ATA', 'AA19BAA', 'AA19GAA', 'AA19AJA', 'AA19ZAA', 'AA19AGA', 'AA19AUA', 'AA19ALA', 'AA19MAA', 'AA19AAR'})
        self.assertEqual(_find_missing_chars(input), expected_output)

    def test_find_missing_chars_2(self):
        # Test the _find_missing_chars function
        # Test if the input is an empty string
        # An empty string is missing all characters
        input = ''
        expected_output = (396725472, set())
        self.assertEqual(_find_missing_chars(input), expected_output)

if __name__ == '__main__':
    unittest.main()