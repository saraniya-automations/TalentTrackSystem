from marshmallow import Schema, fields

class UserSchema(Schema):
    name = fields.Str(required=True)
    email = fields.Email(required=True)
    role = fields.Str(required=True)
