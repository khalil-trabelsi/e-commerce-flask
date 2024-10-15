import re
import os

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}


def get_upload_folder():
    match = re.search(r'(.*src)', os.path.abspath(__file__))
    return os.path.join(os.path.dirname(match.group(1)), 'static', 'images')


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

