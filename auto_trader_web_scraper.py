import bs4
import time
import shutil
import os.path
import numpy as np
import urllib.request
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class ImageNotFoundError(Exception):
    '''
    Custom error to be raised when an image cannot be found
    '''
    pass


def create_driver_od():
    '''
    Function to create and set up a chrome driver object
    :return: Returns a chrome driver object
    '''
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument(
        f"--user-agent={'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36'}")
    return webdriver.Chrome(options=options)


def get_page(url, delay=5):
    '''
    Function to get the content of a page and return it as a bs4 object
    :param url: url of the page to get
    :param delay: delay in seconds to wait for the page to load
    :return: bs4 object of the page content
    '''
    driver = create_driver_od()
    # open the provided URL using the global chrome driver
    driver.get(url)

    # sleep for the requested number of seconds to allow the page to fully load dynamic content
    time.sleep(delay)

    # return a bs4 object of the HTML (it's more efficient to parse a bs4 object than a string)
    res = bs4.BeautifulSoup(driver.page_source, "lxml")

    # close the driver as it has completed its task
    driver.close()
    return res


def get_makes():
    '''
    Function to get and filter through all the makes of cars on the autotrader website
    :return: array of makes that have more than 5000 listings
    '''
    # create an empty array to store makes temporarily
    res = []

    # get the content of the autotrader home page as a bs4 object using the get_page function
    bs4content = get_page('https://www.autotrader.co.uk/', 5)

    # find all option tags within the optgroup tag labelled 'All makes' (part of the search form on the home page)
    options = bs4content.find('optgroup', label='All makes').find_all('option')

    # iterate through all makes and store allowed makes into the res array
    for option in options:

        text = option.get_text()
        quantity = int(text[text.find('(') + 1:text.find(')')].replace(',', ''))

        # 5000 has 23 makes - at 1500 cars per make - 34500 images
        # 1500 has 30 makes - at 1500 cars per make - 45000 images

        if quantity >= 5000:
            res.append(option['value'])

    # return res
    return res


def get_image_src(listing_id):
    '''
    Function to get the image source URL of a listing
    :param listing_id: id of the listing to get the image from
    :return: string of the image source URL
    '''
    # get the content of the listing and store as bs4 object
    bs4content = get_page('https://www.autotrader.co.uk/car-details/' + listing_id, 5)

    # try to find the meta tag with the property 'og:image', and return the content of the tag
    try:
        return bs4content.find('meta', property='og:image')['content']
    except TypeError:
        pass


def upload_to_bucket(bucket_name, bucket_path, local_path):
    '''
    Function to upload a file to a google cloud storage bucket
    :param bucket_name: name of the bucket to upload to
    :param bucket_path: path to upload the file to within the bucket
    :param local_path: local path of the file to upload
    :return: nothing is returned
    '''
    try:
        # use service account credentials by specifying the private key file.
        storage_client = storage.Client.from_service_account_json('./service_account.json')

        bucket = storage_client.get_bucket(bucket_name)
        blob = bucket.blob(bucket_path)
        blob.upload_from_filename(local_path)
    except Exception:
        pass


def save_image(make, listing_id, location):
    '''
    Function to save an image from a listing to a local directory or a google cloud storage bucket
    :param make: make of the vehicle in the image
    :param listing_id: listing id of the advert holding the image
    :param location: location to save the image to, either 'local' or 'bucket'
    :return: nothing is returned
    '''
    # use the make of the image to construct a path to place the image in
    local_path = ('./data/' + make + '/').replace(' ', '_')
    full_local_path = ('./data/' + make + '/').replace(' ', '_') + listing_id + '.jpg'
    bucket_path = ('data/' + make + '/').replace(' ', '_') + listing_id + '.jpg'

    # if the path does not already exist, create the relevant directories
    if not os.path.exists(local_path):
        os.makedirs(local_path)

    # get the image source URL and save the image into the relevant directory with the name as the listing id
    # try and except is used to catch expired listings
    try:
        src = get_image_src(listing_id)
        if src == '':
            # Raise the custom error
            raise ImageNotFoundError
        urllib.request.urlretrieve(src, local_path + listing_id + '.jpg')

        if location == 'bucket':
            # move image to the bucket
            upload_to_bucket('vmmr-make-bucket', bucket_path, full_local_path)

            # as the image is on the GCS Bucket, it can be removed from the local machine
            os.remove(full_local_path)

    except ImageNotFoundError:
        pass


def find_and_save_listings(make, location, page=1):
    '''
    Function to find and save all listings for a make of car
    :param make: make of the car to find and save listings for
    :param location: location to save the images to, either 'local' or 'bucket'
    :param page: page number to start search, default is 1
    :return: nothing is returned
    '''
    # formulate search URL for make, sorted by relevance, set to the first page
    url = 'https://www.autotrader.co.uk/car-search?make=' + make + '&postcode=WC2N%205DU&sort=relevance&page=' + str(
        page)
    url.replace(' ', '%20')

    # get the content of the page and store is as a bs4 object
    bs4content = get_page(url, 5)

    # find all the listing entries in the HTML
    try:
        listings = bs4content.find('ul', attrs={"data-testid": 'desktop-search'}).findChildren("li", recursive=False)
    except AttributeError:
        pass

    # if the listing is not a paid advert or recommendation, return the listing ID
    for listing in listings:
        if ('>Ad<' in str(listing)) or ('>You may also like<' in str(listing)):
            pass
        else:
            try:
                listing_id = listing.find('section')['id']
                save_image(make, listing_id, location)
            except KeyError:
                pass

    # if the page is 1, get the number of pages and recursively call this function to get listing for other pages
    if page == 1:

        for page in range(2, 100):
            find_and_save_listings(make, location, page)


def initial_cleanup(location):
    '''
    Function to clean up the local data directory and the google cloud storage bucket
    :param location: location to clean up, either 'local' or 'bucket'
    :return: nothing is returned
    '''
    # as part of the initial cleanup, if './data' exists, delete it and all nested directories
    if os.path.exists('./data'):
        print('Wiping Local Data Directory')
        shutil.rmtree('./data', ignore_errors=True)
    os.mkdir('./data')

    # empty the google cloud bucket if the location is 'bucket'
    if location == 'bucket':
        print('Wiping Bucket')
        storage_client = storage.Client.from_service_account_json('./service_account.json')

        bucket = storage_client.get_bucket("vmmr-make-bucket")
        blobs = bucket.list_blobs(prefix='/')
        for blob in blobs:
            blob.delete()


if __name__ == '__main__':
    # Will only work with the location set to 'local' as service account is not provided
    print("Started Program")

    location = 'local'  # This can be set to 'bucket' or 'local'
    initial_cleanup(location)

    print('Getting Makes')
    makes = get_makes()
    print(makes)

    completed = []
    for make in next(os.walk('./data'))[1]:
        completed.append(make)
    print('already completed ' + str(completed))

    # get an array of makes to download
    makes = [i for i in makes if i not in completed]

    print('Finding Listings and Saving Images\n')
    progress = tqdm(makes, colour='green')
    for make in progress:
        progress.set_description(make)
        find_and_save_listings(make, location)

    print('Program Complete')
