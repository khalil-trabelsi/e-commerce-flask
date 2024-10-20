ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}


def get_upload_folder():
    from app import app
    return app.config['UPLOAD_FOLDER']


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

