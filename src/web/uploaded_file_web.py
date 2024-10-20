
from flask_restx import Resource, Namespace
from flask import send_from_directory

uploaded_file_api = Namespace('static', description='Get Uploaded files')


@uploaded_file_api.route('/uploads/<string:filename>')
class UploadedFile(Resource):
    @uploaded_file_api.response(200, 'Success')
    def get(self, filename):
        from app import app
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)