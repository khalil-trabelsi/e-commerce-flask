from marshmallow import EXCLUDE, fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from sqlalchemy import Uuid
from db import db
from datetime import date, datetime, UTC


class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(80), unique=True, nullable=False)
    user = db.relationship('User', back_populates='role')

    def __repr__(self):
        return self.label



class TokenBlockList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(Uuid, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(UTC))

    def __repr__(self):
        return '<TokenBlockList %r>' % self.jti


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.Text(), nullable=False)
    birth_date = db.Column(db.Date, nullable=False)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    phone_number = db.Column(db.String(80), nullable=False)
    token = db.Column(db.Text(), nullable=True)
    role = db.relationship('Role', lazy='joined', uselist=False, back_populates='user')
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=date.today)
    updated_at = db.Column(db.DateTime, nullable=False, default=date.today)
    gender = db.Column(db.String(20), nullable=False)

    def __init__(self, email, password, birth_date, first_name, last_name, phone_number, gender, role=2):
        self.email = email
        self.password = password
        self.birth_date = birth_date
        self.first_name = first_name
        self.last_name = last_name
        self.phone_number = phone_number
        self.token = ""
        self.created_at = date.today()
        self.updated_at = date.today()
        self.role_id = role
        self.gender = gender

    def __repr__(self):
        return '%r<User %r %r>' % (self.email, self.role_id, self.role)

    def revoke_refresh_token(self):
        self.token = None
        db.session.commit()


class RoleSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Role
        unknown = EXCLUDE
        register = True


class UserSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = User
        unknown = EXCLUDE
        register = True

    role = fields.Nested("RoleSchema")