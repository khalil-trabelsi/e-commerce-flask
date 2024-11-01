from marshmallow import fields, Schema, EXCLUDE

from src.models.user import UserSchema


class LoginArgsSchema(Schema):
    email = fields.Str(required=True)
    password = fields.Str(required=True)

    class Meta:
        unknown = EXCLUDE


class CustomerPostArgsSchema(Schema):
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


class AdminPostArgsSchema(Schema):
    username = fields.Str(required=True)
    email = fields.Str(required=True)
    password = fields.Str(required=True)
    gender = fields.Str(required=True)
    role_id = fields.Integer(required=True)
    phone_number = fields.Str(required=True)
    birth_date = fields.Str(required=True)

    class Meta:
        unknown = EXCLUDE


class UserPutArgsSchema(Schema):
    first_name = fields.Str(required=False)
    last_name = fields.Str(required=False)
    email = fields.Str(required=False)
    gender = fields.Str(required=False)
    role_id = fields.Integer(required=False)
    phone_number = fields.Str(required=False)
    birth_date = fields.DateTime(required=False)
    status = fields.Str(required=False)
    username = fields.Str(required=False)
    
    class Meta:
        unknown = EXCLUDE


class SupplierPutArgsSchema(Schema):
    name = fields.Str(required=False)
    contact_name = fields.Str(required=False)
    email = fields.Str(required=False)
    phone = fields.Str(required=False)
    address = fields.Str(required=False)
    city = fields.Str(required=False)
    zipcode = fields.Str(required=False)
    country = fields.Str(required=False)

    class Meta:
        unknown = EXCLUDE


class CategoryPostArgsSchema(Schema):
    name = fields.Str(required=True)
    description = fields.Str(required=False)
    parent_id = fields.Integer(required=False)

    class Meta:
        unknown = EXCLUDE


class CategoryPutArgsSchema(Schema):
    name = fields.Str(required=False)
    description = fields.Str(required=False)
    parent_id = fields.Integer(required=False)

    class Meta:
        unknown = EXCLUDE


class ProductImagePostArgsSchema(Schema):
    files = fields.List(fields.Raw(required=True, type='file'), required=True)


class StockMovementFilterArgsSchema(Schema):
    suppliers_id = fields.List(fields.Integer(), required=False)
    products_id = fields.List(fields.Integer(), required=False)


class UserGetSchema(UserSchema):
    first_name = fields.Str(required=False)
    last_name = fields.Str(required=False)
    phone_number = fields.Str(required=False)
    birth_date = fields.Str(required=False)
    username = fields.Str(required=False)


class ShippingAddressPutSchema(Schema):
    street = fields.Str(required=False)
    city = fields.Str(required=False)
    country = fields.Str(required=False)
    postal = fields.Str(required=False)