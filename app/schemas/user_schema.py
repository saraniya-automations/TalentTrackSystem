from marshmallow import Schema, fields

class UserSchema(Schema):
    name = fields.Str(required=True)
    email = fields.Email(required=True)
    role = fields.Str(required=True)
    phone = fields.Str(required=False)
    department = fields.Str(required=False)
    password = fields.Str(required=True, load_only=True)  # Required at creation
    status = fields.Str(required=False)  # ✅ Add this line

class UserUpdateSchema(Schema):
    name = fields.Str(required=True)
    email = fields.Email(required=True)
    role = fields.Str(required=True)
    phone = fields.Str(required=False)
    department = fields.Str(required=False)
    password = fields.Str(required=False, load_only=True)  # Optional on update
    status = fields.Str(required=False)