from marshmallow import fields, Schema, EXCLUDE


class LoginArgsSchema(Schema):
    email = fields.Str(required=True)
    password = fields.Str(required=True)

    class Meta:
        unknown = EXCLUDE


class UserPostArgsSchema(Schema):
    first_name = fields.Str(required=True)
    last_name = fields.Str(required=True)
    email = fields.Str(required=True)
    password = fields.Str(required=True)
    gender = fields.Str(required=True)
    role_id = fields.Integer(required=True)
    phone_number = fields.Str(required=True)
    birth_date = fields.Str(required=True)

    class Meta:
        unknown = EXCLUDE


class UserPutArgsSchema(Schema):
    first_name = fields.Str(required=True)
    last_name = fields.Str(required=True)
    email = fields.Str(required=True)
    gender = fields.Str(required=True)
    role_id = fields.Integer(required=True)
    phone_number = fields.Str(required=True)
    birth_date = fields.Str(required=True)

    class Meta:
        unknown = EXCLUDE