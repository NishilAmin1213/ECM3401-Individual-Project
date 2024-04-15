import re
import itertools
from ves import query_VES

def tune_plate(plate):
    # the number plate length must be 7
    if len(plate) == 7:

        # as the number plate is the correct length
        # convert any characters that have been read in wrong
        res = ''
        for character, index in zip(plate, range(len(plate))):
            if index in [2, 3]:
                # the character must be a number
                if not character.isnumeric():
                    # character is not a number, so convert it if possible
                    character = convert(character)
                    pass
            else:
                # the character must be a letter
                if not character.isalpha():
                    # character is not a letter, so convert it if possible
                    character = convert(character)
                    pass

            # add the character to the result string
            res += character

        # ensure that the pattern matches the regex, if it doesn't, return the original plate
        pattern = re.compile(r"[A-Z][A-Z][0-9][0-9][A-Z][A-Z][A-Z]")
        if not pattern.match(res):
            return plate

        # if we reach here, the res is a valid number plate, return res
        return res

    # if we reach here, the plate is not 7 characters long, therefore cannot be tuned
    # return the original plate
    return plate

#NOTE - potentialy tune plate can return multiple plates - becasue of the issue with O and 0
# IF GJ07HPW has a missing J, it can be read as GO_7HPW or G_07HPW - which makes a difference on success of prediction


def validate_plate(plate):
    # the number plate length must be 7
    if len(plate) != 7:
        # the number plate is too long or too short, return False
        return False

    # the number plate must match the regex LLNNLLL
    pattern = re.compile(r"[A-Z][A-Z][0-9][0-9][A-Z][A-Z][A-Z]")
    if not pattern.match(plate):
        # the number plate does not follow the regex, return False
        return False

    # number plate area code cannot contain I, Q or Z
    area_code = plate[:2]
    if 'I' in area_code or 'Q' in area_code or 'Z' in area_code:
        # the area code is invalid, return False
        return False

    # the number in the plate must be in valid_years
    # these are 01-09, 51-59, 10-19, 60-69, 20-24, 70-74
    # char1 must be 0, 1, 2, 5, 6, 7
    # char2 must be 0-9
    plate_year = plate[2:4]
    if (plate_year[0] not in '012567') or (plate_year[1] not in '0123456789'):
        # the year of the number plate is not valid, return False
        return False

    # the final three characters of the plate cannot contain an I or Q
    final_three = plate[4:]
    if 'I' in final_three or 'Q' in final_three:
        # the final three characters are invalid, return False
        return False

    # if we reach this point, then the plate is valid
    return True


def convert(char):
    # define a dictionary of mappings between letters and numbers
    map_dict = {'O': '0',
                '0': 'O',
                'I': '1',
                '1': 'I',
                'S': '5',
                '5': 'S'}
    try:
        # try to change the incorrect character to the matching number or vice versa
        print('Changing: \'' + char + '\' to \'' + map_dict[char] + '\'')
        # return the new character
        return map_dict[char]
    except KeyError:
        # if there is an error in doing so, the letter cannot be converted, so return the origninal character
        return char


def get_combos(text, length):
    res = []
    for i in range(len(text) - (length-1)):
        res.append(text[i:i+length])
    return res


def fill_blank(text, options):
    res = []
    for char in options:
        # add the string with the replaced '?' to the res array
        res.append(text.replace('?', char))
    return res


def check_or_correct_area_code(area_code):
    # store results in a set to avoid duplicates
    res = set()

    if len(area_code) >= 2:
        # if the area code is too long, add options of the correct length using permutations of the characters provided
        res.update(get_combos(area_code, 2))
    elif len(area_code) == 1:
        # there is one character missing which could be before or after the existing one
        # add the possible options of the correct length including the character provided
        # character options are A-Z minus I, Q and Z
        res.update(fill_blank('?' + area_code, 'ABCDEFGHJKLMNPRSTUVWXY'))
        res.update(fill_blank(area_code + '?', 'ABCDEFGHJKLMNPRSTUVWXY'))

    # return the res set - this holds possible options for the area code
    return res


def check_or_correct_final_three(final_three):
    # stores results in a set to avoid duplicates
    res = set()

    if len(final_three) >= 3:
        # if the area code is too long, add options of the correct length using permutations of the characters provided
        res.update(get_combos(final_three, 3))
    elif len(final_three) == 2:
        # there is one character missing which could be before or after or in between the existing ones
        # add the possible options of the correct length including the character provided
        # character options are A-Z minus I and Q
        res.update(fill_blank('?' + final_three, 'ABCDEFGHJKLMNPRSTUVWXYZ'))
        res.update(fill_blank(final_three + '?', 'ABCDEFGHJKLMNPRSTUVWXYZ'))
        res.update(fill_blank(final_three[0] + '?' + final_three[1], 'ABCDEFGHJKLMNPRSTUVWXYZ'))

    # return the res set - this holds possible options for the final three characters
    return res


def check_or_correct_year(year):
    # stores results in a set to avoid duplicates
    res = set()

    if len(year) >= 2:
        # the year is too long - get all permutation of pairs from it
        res.update(get_combos(year, 2))
    elif len(year) == 1:
        # there is one character missing which could be before or after the existing one
        # add the possible options of the correct length including the character provided
        # character options are 012567 for the first character and 0-9 for the second character
        res.update(fill_blank('?' + year, '012567'))
        res.update(fill_blank(year + '?', '0123456789'))
    else:
        # no year was found, so return all possible years - hard coded in an array as this does not change
        res.update(['00', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15',
                     '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '51', '52',
                     '53', '54', '55', '56', '57', '58', '59', '60', '61', '62', '63', '64', '65', '66', '67', '68',
                     '69', '70', '71', '72', '73', '74'])

    # return the res set - this holds possible options for the year
    return res


def find_missing_chars(invalid_plate):
    print('finding missing characters')
    res = []
    # We know that I cannot be found in a number plate, therefore if an I is found, replace it with a 1
    # NOTE - second plate with O and 0 swapped can be placed in array here and the next block iterated over
    invalid_plate = invalid_plate.replace('I', '1')

    try:
        # try to find two numbers in the string
        pattern = re.compile(r"\d\d")
        int_index = pattern.search(invalid_plate).span()
    except AttributeError:
        # two numbers were not found, therefore try to look for one number
        try:
            pattern = re.compile(r"\d")
            int_index = pattern.search(invalid_plate).span()
        except AttributeError:
            # one number was not found, therefore there are no numbers in the number plate
            # place the split at index 2
            int_index = (2, 2)

    # split the number plate into 3 components
    left = invalid_plate[:int_index[0]]
    centre = invalid_plate[int_index[0]:int_index[1]]
    right = invalid_plate[int_index[1]:]

    print(left)
    print(centre)
    print(right)

    # check or correct each component of the number plate
    left = check_or_correct_area_code(left)
    centre = check_or_correct_year(centre)
    right = check_or_correct_final_three(right)

    # get the number of permutations of results
    cartesian_product = itertools.product(left, centre, right)
    num_permutations = len(list(cartesian_product))
    print(str(num_permutations) + ' permutations')
    # if there are too many computations this will not be time efficient
    # or efficient for the usage of the VES Database
    if num_permutations == 0 or num_permutations > 115:
        # it is not possible to produce a result
        print('Too Many Permutations')
        return []

    # add every combination of the three components to the res array
    for combo in itertools.product(left, centre, right):
        res.append(combo[0] + combo[1] + combo[2])

    # return all possible options for the number plate
    return res


# this function is when a plate is valid, but does not match the vehicle characteristics
def full_plate_match(plate):
    res = []
    # for each character in the array
    for index in range(len(plate)):
        # replate the character with a ?
        tmp = plate[:index] + '?' + plate[index+1:]
        index = str(index)
        # based on the index of the '?' get all possible values it can be and plate it into the plate
        if index in '01':
            # the area code
            res = res + fill_blank(tmp, 'ABCDEFGHJKLMNPRSTUVWXY')
        elif index in '456':
            # the last 3 letters
            res = res + fill_blank(tmp, 'ABCDEFGHJKLMNPRSTUVWXYZ')
        elif index in '2':
            # the first number
            res = res + fill_blank(tmp, '012567')
        else:
            # the second number
            res = res + fill_blank(tmp, '0123456789')

    # return res - all combinations of plates possible by changing one letter at a time
    return res


def filter_all_guesses(color, make, all_guesses):
    # score matching guesses in the array
    correct_guesses = []
    # check each plate in the array provided
    for plate in all_guesses:
        # get the plate details from VES
        test_plate_details = query_VES(plate)
        try:
            if test_plate_details['ves_make'] == make and test_plate_details['ves_color'] == color:
                # if the plate make and color match the characteristics passed in, append the plate to the correct_guesses array
                print('FOUND: ' + plate)
                correct_guesses.append(plate)
        except KeyError:
            # if there is a KeyError, VES could not find the plate, so continue checking other plates
            pass

    # return all correct guesses
    return correct_guesses


def process_plate(res, plate_data):
    if plate_data['reg_found']:
        # the plate could have incorrect I's or O's based on position, so we can run it through the tune function
        plate_data['reg_text'] = tune_plate(plate_data['reg_text'])

        if validate_plate(plate_data['reg_text']):
            # plate has a valid format
            ves_data = query_VES(plate_data['reg_text'])

            if not ves_data['ves_found']:
                # no data existed on ves, therefore make make and color blank
                # this prevents an error in the next if statement
                ves_data.update({'ves_make': '', 'ves_color': ''})

            if ves_data['ves_make'] == res['predicted_make'] and ves_data['ves_color'] == res['predicted_color']:
                # plate matches vehicle details on VES
                # display the data

                plate_status = 'Read Correctly - No Changes Made'
            else:
                # plate is valid, but does not match vehicle details
                # alter plate to see if we can find a match
                print('WORK IN PROGRESS')

                all_guesses = full_plate_match(plate_data['reg_text'])
                correct_guesses = filter_all_guesses(res['predicted_color'], res['predicted_make'], all_guesses)

                if len(correct_guesses) >= 1:
                    # one or more valid guesses were found
                    plate_status = str(len(correct_guesses)) + ' plate(s) predicted ' + str(correct_guesses)
                    ves_data = query_VES(correct_guesses[0])

                else:
                    plate_status = 'Plate Read - Does Not Match Vehicle'
                    ves_data = {'ves_found': False}

        else:
            # plate format is incorrect
            # send the plate through find_missing_chars
            all_guesses = find_missing_chars(plate_data['reg_text'])
            correct_guesses = filter_all_guesses(res['predicted_color'], res['predicted_make'], all_guesses)

            if len(correct_guesses) >= 1:
                # one or more valid guesses were found
                plate_status = str(len(correct_guesses)) + ' plate(s) predicted ' + str(correct_guesses)
                ves_data = query_VES(correct_guesses[0])

            else:
                # no valid plates were found
                plate_status = 'No Valid Guesses Found'
                ves_data = {'ves_found': False}
    else:
        # plate was not read in successfully - it may not exist or may not be very visible
        ves_data = {'ves_found': False}
        plate_status = 'No Plate Found'

    return plate_data, ves_data, plate_status
