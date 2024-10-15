from flask_restx import Resource, Namespace
from marshmallow_jsonschema import JSONSchema

from src.models.user import Role, RoleSchema

role_api = Namespace('roles', description='Roles')


role_schema = RoleSchema()
role_model = role_api.schema_model(
    'roleModel',
    JSONSchema().dump(role_schema)['definitions']['RoleSchema']
)


@role_api.route('')
class RoleWeb(Resource):
    @role_api.response(200, 'Success', role_model)
    def get(self):
        roles = Role.query.all()
        return {'roles': roles}, 200
