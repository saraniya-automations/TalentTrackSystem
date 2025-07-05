from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.utils.auth import role_required
from app.schemas.salary_schema import SalaryRecordSchema
from app.service.salary_service import SalaryService
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from app.models.user import User
import csv
from datetime import datetime, timedelta

salary_bp = Blueprint('salary', __name__)
salary_service = SalaryService()
salary_schema = SalaryRecordSchema()

@salary_bp.route('/salary/add', methods=['POST'])
@jwt_required()
@role_required('Admin')
def add_salary_record():
    data = request.get_json()
    errors = salary_schema.validate(data)
    if errors:
        return jsonify({"errors": errors}), 400
    try:
        salary_service.add_salary_record(data)
        return jsonify({'message': 'Salary record added successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@salary_bp.route('/salary/my-records', methods=['GET'])
@jwt_required()
def view_my_salary():
    identity = get_jwt_identity()
    employee_id = identity['employee_id']
    month = request.args.get('month')

    if month:
        record = salary_service.get_salary_by_month(employee_id, month)
        return jsonify(record or {"message": "No record found"}), 200
    else:
        records = salary_service.get_all_salary(employee_id)
        return jsonify(records), 200

@salary_bp.route('/salary/my-records/payslip', methods=['GET'])
@jwt_required()
def download_payslip():
    month = request.args.get('month')
    if not month:
        return jsonify({"message": "Month (YYYY-MM) is required as a query parameter"}), 400

    identity = get_jwt_identity()
    current_user_email = identity['email']

    user_model = User()
    user = user_model.get_by_email(current_user_email)

    if not user:
        return jsonify({"message": "Employee not found"}), 404

    employee_id = user['employee_id']
    record = salary_service.get_salary_by_month(employee_id, month)

    if not record:
        return jsonify({"message": "No salary record found for the specified month"}), 404

    # Generate PDF
    pdf_buffer = BytesIO()
    p = canvas.Canvas(pdf_buffer, pagesize=A4)
    p.setFont("Helvetica", 12)

    p.drawString(50, 800, f"Payslip for: {user['name']} ({employee_id})")
    p.drawString(50, 780, f"Month: {record['salary_month']}")
    p.drawString(50, 760, f"Basic Salary: {record['basic_salary']} {record['currency']}")
    p.drawString(50, 740, f"Bonus: {record['bonus']} {record['currency']}")
    p.drawString(50, 720, f"Deductions: {record['deductions']} {record['currency']}")
    p.drawString(50, 700, f"Net Pay: {record['direct_deposit_amount']} {record['currency']}")
    p.drawString(50, 680, f"Pay Frequency: {record['pay_frequency']}")

    p.showPage()
    p.save()
    pdf_buffer.seek(0)

    filename = f"Payslip_{employee_id}_{month}.pdf"

    return send_file(
        pdf_buffer,
        mimetype='application/pdf',
        download_name=filename,
        as_attachment=True
    )


@salary_bp.route('/salary/employee/<employee_id>', methods=['GET'])
@jwt_required()
@role_required('Admin')
def get_employee_salary_records(employee_id):
    month = request.args.get('month')

    if month:
        record = salary_service.get_salary_by_month(employee_id, month)
        return jsonify(record or {"message": "No record found"}), 200
    else:
        records = salary_service.get_all_salary(employee_id)
        return jsonify(records), 200

@salary_bp.route('/salary/employee', methods=['GET'])
@jwt_required()
@role_required('Admin')
def get_all_salary_records():
     # Get pagination parameters from query string
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=10, type=int)
    # Get paginated results
    result = salary_service.get_all_employees_salary_records(page, per_page)
    return jsonify(result)
    

@salary_bp.route('/salary/export-pdf', methods=['GET'])
@jwt_required()
@role_required('Admin')
def export_salary_records_pdf():
    employee_id = request.args.get('employee_id')  # Optional
    month = request.args.get('month')  # Optional

    records = salary_service.get_filtered_salary_records(employee_id, month)

    if not records:
        return jsonify({"message": "No records found"}), 404

    pdf_buffer = BytesIO()
    p = canvas.Canvas(pdf_buffer, pagesize=A4)
    width, height = A4
    p.setFont("Helvetica-Bold", 14)
    p.drawString(200, height - 40, "Salary Records Report")

    p.setFont("Helvetica", 10)
    y = height - 70
    headers = ["Emp ID", "Name", "Month", "Basic", "Bonus", "Deductions", "Net Pay", "Currency"]
    col_widths = [60, 100, 60, 50, 50, 60, 60, 50]
    x_positions = [50, 110, 210, 270, 320, 370, 440, 500]

    # Draw header
    for i, header in enumerate(headers):
        p.drawString(x_positions[i], y, header)
    y -= 20

    for record in records:
        if y < 50:  # Start a new page if space runs out
            p.showPage()
            y = height - 50
            p.setFont("Helvetica", 10)

        values = [
            record['employee_id'],
            record.get('name', 'N/A'),
            record['salary_month'],
            str(record['basic_salary']),
            str(record['bonus']),
            str(record['deductions']),
            str(record['direct_deposit_amount']),
            record['currency']
        ]
        for i, value in enumerate(values):
            p.drawString(x_positions[i], y, value)
        y -= 20

    p.save()
    pdf_buffer.seek(0)

    return send_file(
        pdf_buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name='salary_records_export.pdf'
    )

@salary_bp.route('/salary/countdown', methods=['GET'])
@jwt_required()
def salary_countdown():
    identity = get_jwt_identity()
    employee_id = identity['employee_id']

    latest_salary = salary_service.get_latest_salary(employee_id)
    if not latest_salary:
        return jsonify({"message": "No salary record found"}), 404

    # Calculate next payday
    year, month = map(int, latest_salary['salary_month'].split('-'))
    today = datetime.now().date()
    payday = datetime(year, month, 1).replace(day=28) + timedelta(days=4)
    payday = (payday - timedelta(days=payday.day)).date()  # last day of the month as date

    days_remaining = (payday - today).days

    return jsonify({
        "next_payday": payday.strftime('%Y-%m-%d'),
        "days_remaining": max(days_remaining, 0),
        "expected_amount": latest_salary['direct_deposit_amount'],
        "pay_frequency": latest_salary['pay_frequency']
    }), 200