# app/schemas/leave_schema.py

from marshmallow import Schema, fields

class LeaveApplySchema(Schema):
    leave_type = fields.Str(required=True)
    start_date = fields.Date(required=True)
    end_date = fields.Date(required=True)
    reason = fields.Str(required=True)

class LeaveStatusUpdateSchema(Schema):
    status = fields.Str(required=True)
