from ast import literal_eval

from flask import Flask, jsonify, render_template, request, Response

from scripts.downloader import download_hashes
from scripts.checks import check_info

app = Flask(__name__)


@app.route('/check/')
def check():
    """
    Does the following checks:
        - The album hash (album_hash) is 5 characters long
        - The album exists (a get request gives a 200)
        - The album exists and has images (some have 0 images)
        - The .ini file exists (relative to cwd aka directory this file is in)
        - If the new directory option was checked:
            - Will attempt to make the new directory
        - If it isn't checked:
            - The chosen directory exists
            - If the empty directory option was checked:
                - The chosen directory is also empty
    If it passes these checks, the list of the image URLs are passed back.
    Otherwise, a response is passed back that triggers an alert and doesn't
    follow through with the download.
    """
    new_dir = literal_eval(request.args.get('new_dir'))
    empty_dir = literal_eval(request.args.get('empty_dir'))
    img_dir = request.args.get('img_dir')
    album_hash = request.args.get('album_hash')

    response, img_list = check_info(new_dir, empty_dir, img_dir, album_hash)

    return jsonify(response=response, img_list=img_list)


@app.route('/download_album/<hash_id>')
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

    return Response(download_hashes(album_hash, img_dir, hash_id, img_list),
                    mimetype='text/event-stream')


@app.route('/')
def index():
    return render_template('main.html')


if __name__ == '__main__':
    app.debug = True
    app.run(threaded=True)
