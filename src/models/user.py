from marshmallow import EXCLUDE, fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from sqlalchemy import Uuid
from db import db
from datetime import date, datetime, UTC, timezone


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
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.Text(), nullable=False)
    token = db.Column(db.Text(), nullable=True)
    role = db.relationship('Role', lazy='joined', uselist=False, back_populates='user')
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now(timezone.utc))
    gender = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), nullable=True)
    is_confirmed = db.Column(db.Boolean, nullable=False, default=False)
    confirmed_on = db.Column(db.DateTime, nullable=True)

    __mapper_args__ = {
        'polymorphic_identity': 0,
        'polymorphic_on': role_id
    }

    def __init__(self, email, password, gender, role_id, is_confirmed=False, confirmed_on=None):
        self.email = email
        self.password = password
        self.token = ""
        self.role_id = role_id
        self.gender = gender
        self.status = "active"
        self.is_confirmed = is_confirmed
        self.confirmed_on = confirmed_on

    def __repr__(self):
        return '%r<User %r>' % (self.email, self.role_id)

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