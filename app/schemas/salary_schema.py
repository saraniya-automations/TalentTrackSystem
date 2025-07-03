from marshmallow import Schema, fields, validate

class SalaryRecordSchema(Schema):
    employee_id = fields.Str(required=True)
    salary_month = fields.Str(required=True, validate=validate.Regexp(r'^\d{4}-\d{2}$'))  # YYYY-MM format
    basic_salary = fields.Float(required=True)
    bonus = fields.Float(load_default=0)
    deductions = fields.Float(load_default=0)
    currency = fields.Str(load_default='NZD')
    pay_frequency = fields.Str(load_default='Monthly')
    direct_deposit_amount = fields.Float(load_default=None)