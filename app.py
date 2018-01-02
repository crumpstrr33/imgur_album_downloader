from ast import literal_eval
import os
import json

from requests import get
from flask import Flask, jsonify, render_template, request, Response

import downloader as dler

app = Flask(__name__)


@app.route('/check/')
def check():
    """
    Does checks based on what's checked. If a new directory is checked, it will
    make sure that directory doesn't already exist and then create it. If empty
    directory is checked, it will make sure the chosen directory is empty. It
    will also make sure the .ini file exists which should be in the same
    directory as this file. For any error, an alert will be shown to the user
    and nothing will be downloaded.
    """
    new_dir = literal_eval(request.args.get('new_dir'))
    empty_dir = literal_eval(request.args.get('empty_dir'))
    img_dir = request.args.get('img_dir')
    album_hash = request.args.get('album_hash')

    # Check to make sure hash is 5 letters long
    if len(album_hash) != 5:
        return jsonify(response='wrong_len_hash', img_list=None)

    # Check to make sure album exists
    if get('https://imgur.com/a/' + album_hash).status_code == 404:
       return jsonify(response='dne_album', img_list=None)

    # Check that it's not a 0 picture album
    img_list = dler._get_album_info(album_hash)
    if not len(img_list):
        return jsonify(response='zero_imgs', img_list=None)

    # Check to make sure .ini exists
    if not os.path.isfile(os.path.join(os.getcwd(), 'imgur_api_info.ini')):
        return jsonify(response='dne_ini', img_list=None)

    # Will not check if parent directory exists since the grandparent or
    # great-grandparent, etc. could exist and that still works
    if new_dir:
        try:
            os.makedirs(img_dir)
        except FileExistsError:
            return jsonify(response='new_dir_exists', img_list=None)
    else:
        # If not, make sure current directory exists
        if not os.path.isdir(img_dir):
            return jsonify(response='dne_dir', img_list=None)
        # Then check to make sure it's not empty if checkbox was checked
        elif empty_dir and os.listdir(img_dir):
            return jsonify(response='nonempty_dir', img_list=None)

    return jsonify(response='', img_list=img_list)


@app.route('/download_album/<hash_id>', methods=['GET', 'POST'])
def download_album(hash_id):
    """
    Downloads the album and returns info to the front such as current pic
    number downloaded, total to be downloaded and so on.
    """
    album_hash = request.args.get('album_hash')
    img_dir = request.args.get('img_dir')
    new_dir = literal_eval(request.args.get('new_dir'))
    empty_dir = literal_eval(request.args.get('empty_dir'))
    img_list = literal_eval(request.args.get('img_list'))

    return Response(dler.download_hashes(album_hash, img_dir, hash_id, img_list),
                    mimetype='text/event-stream')


@app.route('/')
def index():
    return render_template('main.html')


if __name__ == '__main__':
    app.debug = True
    app.run(threaded=True)
