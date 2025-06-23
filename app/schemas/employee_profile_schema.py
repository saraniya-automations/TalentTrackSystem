# app/schemas/employee_profile_schema.py
from marshmallow import Schema, fields

class EmployeeProfileSchema(Schema):
    middle_name = fields.Str()
    nickname = fields.Str()
    other_id = fields.Str()
    license_number = fields.Str()
    license_expiry_date = fields.Str()
    nationality = fields.Str()
    marital_status = fields.Str()
    date_of_birth = fields.Str()
    gender = fields.Str()