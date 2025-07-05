from marshmallow import Schema, fields, validate

class CompletionSubmissionSchema(Schema):
    department = fields.Str(required=True)
    course_name = fields.Str(required=True)
    completion_note = fields.Str(required=False)
    file_path = fields.Str(required=False)
    completed_at = fields.DateTime(required=True)


class ReviewSchema(Schema):
    status = fields.Str(
        required=True,
        validate=validate.OneOf(["Approved", "Rejected"])
    )
    rating = fields.Str(
        required=True,
        validate=validate.OneOf(["Excellent", "Good", "Average", "Below Average", "Poor", "1", "2", "3", "4", "5"])
    )
    admin_comment = fields.Str(required=True)