import os.path
import random
import tempfile

from flask import Flask, request
from flask import send_file
from xkcdpass import xkcd_password as xp

from handler.pdf_handler import PdfHandler

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), "static"))

PORT = 1213


handler = PdfHandler()


def random_string(n):
    wordfile = xp.locate_wordfile()
    mywords = xp.generate_wordlist(wordfile=wordfile, min_length=5, max_length=8)
    words = xp.generate_xkcdpassword(mywords, numwords=n).split()
    return "".join(map(str.capitalize, words)) + str(random.randint(0, 100))


@app.route('/', methods=['GET'])
def get_info():
    """
    Root URL '/' is need start with simple Flask before rest-plus.API otherwise you will get 404 Error.
    It is bug of rest-plus lib.
    """
    path = "form_input.html"
    return app.send_static_file(path)


@app.route('/static_file', methods=['GET'])
def get_static_file():
    file = request.values["fname"]
    return app.send_static_file(file)


@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files or request.files['file'] is None or request.files['file'].filename == "":
        raise ValueError("Error: Missing content in request_post file parameter")
    file = request.files['file']
    if not file.filename.endswith(".pdf"):
        raise ValueError("Bad file format {}".format(file.filename))
    with tempfile.TemporaryDirectory() as tmpdir:
        name = random_string(3) + ".pdf"
        path_file = os.path.join(tmpdir, name)
        file.save(path_file)
        file_out = handler.handle(path_file)
        return send_file(file_out)


def run_api(app: Flask):
    app.run(host='0.0.0.0', port=PORT)


if __name__ == '__main__':
    run_api(app)
