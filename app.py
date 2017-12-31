from ast import literal_eval
import os

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
    response = 'all_good'

    if not os.path.isfile(os.path.join(os.getcwd(), 'imgur_api_info.ini')):
        # Check to make sure .ini exists
        response = 'dne_ini'
    if new_dir:
        # Will not check if parent directory exists since the grandparent or
        # great-grandparent, etc. could exist and that still works
        try:
            os.makedirs(img_dir)
            response = 'new_dir_made'
        except (FileExistsError):
            response = 'new_dir_exists'
    else:
        # If not, make sure current directory exists
        if not os.path.isdir(img_dir):
            response = 'dne_dir'
        # Then check to make sure it's not empty if checkbox was checked
        if empty_dir and os.listdir(img_dir):
            response = 'nonempty_dir'

    return jsonify(response=response)


@app.route('/download_album/<hash_id>/')
def download_album(hash_id):
    """
    Downloads the album and returns info to the front such as current pic
    number downloaded, total to be downloaded and so on.
    """
    album_hash = request.args.get('album_hash')
    img_dir = request.args.get('img_dir')
    new_dir = literal_eval(request.args.get('new_dir'))
    empty_dir = literal_eval(request.args.get('empty_dir'))

    return Response(dler.download_hashes(album_hash, img_dir, hash_id,
                    new_dir, empty_dir), mimetype='text/event-stream')


@app.route('/')
def index():
    return render_template('main.html')


if __name__ == '__main__':
    app.debug = True
    app.run(threaded=True)