import os
from configparser import ConfigParser

import requests


def _get_album_info(album_hash):
    """
    Will obtain and return the image hashes along wit the image file types by
    requesting with the Imgur API where the user tokens are found in a local
    .ini file.
    """
    # Gets info from .ini file
    config = ConfigParser()
    config.read("imgur_api_info.ini")
    info = config["GENERAL"]

    url = "https://api.imgur.com/3/album/{}/images".format(album_hash)

    # Get json for images
    auth = "Bearer {}".format(info["access_token"])
    imgs = requests.get(url, headers={"Authorization": auth})

    # Who needs readability, returns a list of tuples: (img_hash, img_type)
    # img_type is usually '.jpg' or '.png'
    return [
        (
            i["link"][i["link"].index("imgur.com/") + len("imgur.com/") : -4],
            i["link"][-4:],
        )
        for i in imgs.json()["data"]
    ]


def check_info(new_dir, empty_dir, img_dir, album_hash):
    """
    Makes checks on the hash/options chosen/directories chosen, etc. Look at
    the docstring of check.py in app.py for more info.
    """
    # Check to make sure hash is less than 8 letters long
    if len(album_hash) > 7:
        return "wrong_len_hash", None

    # Check to make sure album exists
    if requests.head("https://imgur.com/a/" + album_hash).status_code != 200:
        return "dne_album", None

    # Check that it's not a 0 picture album
    img_list = _get_album_info(album_hash)
    if not len(img_list):
        return "zero_imgs", None

    # Check to make sure .ini exists
    if not os.path.isfile(os.path.join(os.getcwd(), "imgur_api_info.ini")):
        return "dne_ini", None

    # Will not check if parent directory exists since the grandparent or
    # great-grandparent, etc. could exist and that still works
    if new_dir:
        try:
            os.makedirs(img_dir)
        except FileExistsError:
            return "new_dir_exists", None
    else:
        # If not, make sure current directory exists
        if not os.path.isdir(img_dir):
            return "dne_dir", None
        # Then check to make sure it's not empty if checkbox was checked
        elif empty_dir and os.listdir(img_dir):
            return "nonempty_dir", None

    return "", img_list
