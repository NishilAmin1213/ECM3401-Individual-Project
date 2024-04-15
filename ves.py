import json
import requests
# might be good to store the API key in a more secure way


def get_details_VES(reg_no):
    # define the URL to send to send the request to
    url = "https://driver-vehicle-licensing.api.gov.uk/vehicle-enquiry/v1/vehicles"
    # set up the payload json which contians the registration number to query
    payload = "{\n\t\"registrationNumber\": \"" + reg_no + "\"\n}"
    # set up headers for the query, with content type and the API-Key
    headers = {'x-api-key': 'KzGqBg12XW3qV4VKABZHxadF2om7wVSk8MIXZkzj', 'Content-Type': 'application/json'}
    # send the request and store the respone in a variable
    response = requests.request("POST", url, headers=headers, data=payload)
    # return the JSON response encoded as UTF8 if the respone is 200 - OK
    if response.status_code == 200:
        return json.loads(response.text.encode('utf8'))


def query_VES(reg_no):
    # Try to get details from VES using the function above
    # if there are any errors, return a dictionary with 'ves_found' set to False
    try:
        response = get_details_VES(reg_no)
        # return vehicle make, color, mot status and tax status
        res = {'ves_found': True, 'ves_make': response['make'].title(), 'ves_color': response['colour'].title(), 'ves_mot': response['motStatus'], 'ves_tax': response['taxStatus']}
    except Exception:
        res = {'ves_found': False}

    return res
