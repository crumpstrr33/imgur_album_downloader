"""
Imgur is an image sharing website that is used extensively on webistes such as
reddit. On Imgur, albums can be shared that consists of multiple images with a
URL with the form 'https://imgur.com/a/<album hash>' where <album hash> is a
4-character string of numbers and letters.

This code will download a given album through the Imgur API. To create a user
token to use the API, follow the steps at https://api.imgur.com/oauth2. Once an
access token and refresh token are obtained, create a file in the same directory
as this code, call it 'imgur_api_info.ini' and add your tokens like below:

    [GENERAL]
    access_token = somerandomcharacters
    refresh_token = morerandomcharacters
    client_id = whateverthisis
    client_secret = thisthingisalsoneeded
"""
import urllib
import os
from configparser import ConfigParser

import requests


def _get_album_info(album_hash):
    """
    Will obtain and return the image hashes along wit the image file types by
    requesting with the Imgur API where the user tokens are found in a local
    .ini file. If the .ini file isn't found or the code is unsuccessful,
    instead the image info will be obtained by _get_image_hashes.
    """
    # Gets info from .ini file
    config = ConfigParser()
    config.read('imgur_api_info.ini')
    info = config['GENERAL']

    url = 'https://api.imgur.com/3/album/{}/images'.format(album_hash)

    # Get json for images
    auth = 'Bearer {}'.format(info['access_token'])
    imgs = requests.get(url, headers={'Authorization': auth})

    # Who needs readability, returns a list of tuples: (img_hash, img_type)
    # img_type is usually '.jpg' or '.png'
    return [(i['link'][i['link'].index('imgur.com/') + len('imgur.com/'):-4],
             i['link'][-4:]) for i in imgs.json()['data']]


def _check_with_user(string, img_dir):
    """
    Does checking to make sure the user wants to continue for
    different situations.
    """
    while True:
        download = input("The directory '{}' which is ".format(img_dir) +
                         'where the images will be placed ' +
                         string + '. Proceed anyway? [yes|no]\n')
        if download.lower() in ['yes', 'y', 'yeah', 'yup', 'yea']:
            return True
        elif download in ['no', 'n', 'nope', 'oh god no']:
            print('Download aborted.')
            return False


def download_image(img, img_dir):
    """
    Does the actual downloading
    """
    download_url = 'https://i.imgur.com/{}{}'

    # Create the url to download from
    url = download_url.format(*img)

    # Download the iamge to a folder with the imgur image name
    urllib.request.urlretrieve(url, os.path.join(img_dir, img[0]) + img[1])


def _check_token():
    """
    Checks if the current secret token has expired. If it has,
    then use the refresh token to get a new one and replace
    the old one in the ini file.
    """
    # Checks if there is an .ini file
    if not os.path.exists('imgur_api_info.ini'):
        raise IOError('.ini file does not exist')

    # Create parser
    config = ConfigParser()
    config.read('imgur_api_info.ini')
    info = config['GENERAL']

    # Get kwargs for GET
    url = 'https://api.imgur.com/3/credits'
    auth = 'Bearer {}'.format(info['access_token'])
    imgs = requests.get(url, headers={'Authorization': auth})

    # If error 403, then token has expired and if so, get a new one,
    # then try again
    if imgs.status_code == 403:
        print('Current access_token has expired, retrieving a new one...\n')
        new_token = requests.post('https://api.imgur.com/oauth2/token',
                                  data={'refresh_token': info['refresh_token'],
                                        'client_id': info['client_id'],
                                        'client_secret': info['client_secret'],
                                        'grant_type': 'refresh_token'})
        new_access_token = new_token.json()['access_token']

        # Rewrite the .ini file
        config.set('GENERAL', 'access_token', new_access_token)
        with open('imgur_api_info.ini', 'w') as ini_file:
            config.write(ini_file)


def download_hashes(album_hash, img_dir, hash_id):
    """
    This function will download an imgur album. Imgur albums are in the form
    imgur.com/a/<album hash> where <album hash> is some 5 character string.
    Given a 5 character string and a directory this function will download them.

            vvv (Shamelessly stolen from the file docstring) vvv
    This code will download a given album through the Imgur API. To create a
    user token to use the API, follow the steps at https://api.imgur.com/oauth2.
    Once an access token and refresh token are obtained, create a file in the
    same directory as this code, call it 'imgur_api_info.ini' and add your
    tokens like below:

        [GENERAL]
        access_token = somerandomcharacters
        refresh_token = morerandomcharacters
        client_id = whateverthisis
        client_secret = thisthingisalsoneeded
            ^^^ (Shamelessly stolen from the file docstring) ^^^

    Parameters:
    album_hash - The hash of the album to be downloaded.
    img_dirs - The directory to download the album to.
    """
    # Check if we need to get a new token
    _check_token()

    img_dir = os.path.join(*img_dir.split(','))

    try:
        # Get image urls and download them
        img_list = _get_album_info(album_hash)
    except (IOError, KeyError):
        # Can't find .ini file
        yield 'data:{}\nevent:{}\n\n'.format('dne_ini', 'aborted')
        return

    print('\nFound {} images at {}.'.format(
        len(img_list), 'https://imgur.com/a/' + album_hash))

    tot = len(img_list)
    for n, img in enumerate(img_list):
        download_image(img, img_dir)

        data = '{{"total": {}, "count": "{}", "id": "{}"}}'.format(
            tot, str(n + 1), hash_id)

        yield 'data:{}\n\n'.format(data)
        if n == tot - 1:
            yield 'data:{}\nevent:{}\n\n'.format(data, 'finished')
