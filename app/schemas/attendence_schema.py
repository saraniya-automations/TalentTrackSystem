# --- schemas/attendance_schema.py ---
from marshmallow import Schema, fields

class ManualAttendanceSchema(Schema):
    punch_in = fields.String(required=True)
    punch_out = fields.String(required=True)
    date = fields.String(required=True)
    status = fields.String(required=False)
    reason = fields.String(required=False)