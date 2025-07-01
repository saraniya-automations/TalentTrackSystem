# --- schemas/performance_schema.py ---
from marshmallow import Schema, fields

class CourseSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    description = fields.Str()
    type = fields.Str(required=True)
    department = fields.Str()
    target_role = fields.Str()
    deadline = fields.Str()
    created_at = fields.Str(dump_only=True)

class CourseSubmissionSchema(Schema):
    id = fields.Int(dump_only=True)
    employee_id = fields.Str(required=True)
    course_id = fields.Int(required=True)
    completion_notes = fields.Str()
    status = fields.Str(dump_only=True)
    reviewer_comment = fields.Str()
    reviewed_by = fields.Str()
    reviewed_at = fields.Str()
    submitted_at = fields.Str(dump_only=True)
