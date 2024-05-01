# required pip install of selenium, beautifulsoup4, lxml, tqdm, numpy, google-cloud-storage
import bs4
import time
import shutil
import os.path
import numpy as np
import urllib.request
from tqdm import tqdm
from selenium import webdriver
from google.cloud import storage
from selenium.webdriver.chrome.options import Options


class ImageNotFoundError(Exception):
    pass


def create_driver_od():
    # set up and create a chrome driver to be used
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument(
        f"--user-agent={'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36'}")
    return webdriver.Chrome(options=options)


def get_page(url, delay=5):
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
    # get the content of the listing and store as bs4 object
    bs4content = get_page('https://www.autotrader.co.uk/car-details/' + listing_id, 5)

    # try to find the meta tag with the property 'og:image', and return the content of the tag
    try:
        return bs4content.find('meta', property='og:image')['content']
    except TypeError:
        pass


def upload_to_bucket(bucket_name, bucket_path, local_path):

    try:
        # use service account credentials by specifying the private key file.
        storage_client = storage.Client.from_service_account_json('./service_account.json')

        bucket = storage_client.get_bucket(bucket_name)
        blob = bucket.blob(bucket_path)
        blob.upload_from_filename(local_path)
    except Exception:
        pass


def save_image(make, listing_id, location):
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
        urllib.request.urlretrieve(src, local_path+listing_id+'.jpg')

        if location == 'bucket':
            # move image to the bucket
            upload_to_bucket('vmmr-make-bucket', bucket_path, full_local_path)

            # as the image is on the GCS Bucket, it can be removed from the local machine
            os.remove(full_local_path)

    except ImageNotFoundError:
        pass


def find_and_save_listings(make, location, page=1):
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


def move_images(item, path, arr):
    for image in arr:
        # move image into final directory
        src = item + '/' + image
        dest = './data/' + path + '/' + item[7:]

        if not os.path.exists(dest):
            os.makedirs(dest)

        os.replace(src, dest + '/' + image)


def initial_cleanup(location):
    # as part of the initial cleanup, if './data' exists, delete it and all nested directories
    if os.path.exists('./data'):
        print('Wiping Local Data Directory')
        shutil.rmtree('./data', ignore_errors=True)

    # empty the google cloud bucket if the location is 'bucket'
    if location == 'bucket':
        print('Wiping Bucket')
        storage_client = storage.Client.from_service_account_json('./service_account.json')

        bucket = storage_client.get_bucket("vmmr-make-bucket")
        blobs = bucket.list_blobs(prefix='/')
        for blob in blobs:
            blob.delete()


if __name__ == '__main__':
    print("Started Program")

    # not to be run using bucket - this requires a service account json as well as an existing GCS Bucket
    location = 'local' # This can be set to 'bucket' or 'local'
    initial_cleanup(location)

    makes = get_makes()
    print('makes')
    print(makes)

    # idenfity any completed makes - only works when initial cleanup is disabled
    completed = []
    for make in next(os.walk('./data'))[1]:
        completed.append(make)
    print('completed')
    print(completed)

    # filter out any completed makes
    makes = [i for i in makes if i not in completed]
    print('makes-to-do')
    print(makes)

    # find and save all listings for each make
    print('Finding Listings and Saving Images\n')
    progress = tqdm(makes, colour='green')
    for make in progress:
        progress.set_description(make)
        find_and_save_listings(make, location)

    print('Program Complete')
