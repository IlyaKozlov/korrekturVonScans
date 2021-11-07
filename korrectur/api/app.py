import os.path
import tempfile

from flask import Flask, request
from flask import send_file

from handler.pdf_handler import PdfHandler
from utils import random_string

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), "static"))

PORT = 1213

handler = PdfHandler()


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
        return app.response_class(response="Error: Missing content in request_post file parameter",
                                  status=400,
                                  mimetype='text/html;charset=utf-8')
    file = request.files['file']
    if not file.filename.endswith((".pdf", ".djvu")):
        return app.response_class(response="Bad file format {}".format(file.filename),
                                  status=400,
                                  mimetype='text/html;charset=utf-8')

    with tempfile.TemporaryDirectory() as tmpdir:
        file_name, extension = file.filename.rsplit(".", maxsplit=1)
        name = random_string(3) + ".{}".format(extension)
        path_file = os.path.join(tmpdir, name)
        file.save(path_file)
        file_out = handler.handle(path_file)
        return send_file(file_out, as_attachment=True, attachment_filename=file_name + ".pdf")


def run_api(app: Flask):
    app.run(host='0.0.0.0', port=PORT)


if __name__ == '__main__':
    run_api(app)
