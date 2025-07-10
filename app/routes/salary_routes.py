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
from datetime import datetime, timedelta, date

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
    # Get pagination parameters from query string
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=10, type=int)
    
    identity = get_jwt_identity()
    employee_id = identity['employee_id']
    month = request.args.get('month')

    if month:
        record = salary_service.get_salary_by_month(employee_id, month, page, per_page)
        return jsonify(record or {"message": "No record found"}), 200
    else:
        records = salary_service.get_all_salary(employee_id,page, per_page)
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
    records = salary_service.get_salary_by_month_payslip(employee_id, month)

    if not records:
        return jsonify({"message": "No salary record found for the specified month"}), 404

    # Generate PDF
    pdf_buffer = BytesIO()
    p = canvas.Canvas(pdf_buffer, pagesize=A4)
    p.setFont("Helvetica", 12)

    y = 800
    p.drawString(50, y, f"Payslip for: {user['name']} ({employee_id})")
    y -= 20

    # total_basic = 0
    # total_bonus = 0
    # total_deductions = 0
    # total_net = 0

    # for i, rec in enumerate(records, start=1):
    #     basic = rec['basic_salary']
    #     bonus = rec['bonus']
    #     deductions = rec['deductions']
    #     net = rec['direct_deposit_amount']

    #     total_basic += basic
    #     total_bonus += bonus
    #     total_deductions += deductions
    #     total_net += net

    #     p.drawString(50, y, f"Entry {i}: {rec['salary_month']} - {rec['pay_frequency']}")
    #     y -= 20
    #     p.drawString(50, y, f"Basic: {basic} {rec['currency']},")
    #     y -= 20
    #     p.drawString(50, y, f"Bonus: {bonus} {rec['currency']}, Deductions: {deductions} {rec['currency']}, Net: {net} {rec['currency']}")
    #     y -= 30

    # # Summary
    # p.drawString(50, y, "-" * 45)
    # y -= 20
    # p.drawString(50, y, f"Total Basic: {total_basic}")
    # y -= 20
    # p.drawString(50, y, f"Total Bonus: {total_bonus}")
    # y -= 20
    # p.drawString(50, y, f"Total Deductions: {total_deductions}")
    # y -= 20
    # p.drawString(50, y, f"Total Net Pay: {total_net}")
    basic = records['basic_salary']
    bonus = records['bonus']
    deductions = records['deductions']
    net = records['direct_deposit_amount']

    p.drawString(50, y, f"Month: {records['salary_month']} - {records['pay_frequency']}")
    y -= 20
    p.drawString(50, y, f"Basic: {basic} {records['currency']}")
    y -= 20
    p.drawString(50, y, f"Bonus: {bonus} {records['currency']}")
    y -= 20
    p.drawString(50, y, f"Deductions: {deductions} {records['currency']}")
    y -= 20
    p.drawString(50, y, f"Net Pay: {net} {records['currency']}")

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
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=10, type=int)

    if month:
        record = salary_service.get_salary_by_month(employee_id, month,page, per_page)
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

# @salary_bp.route('/salary/countdown', methods=['GET'])
# @jwt_required()
# def salary_countdown():
#     identity = get_jwt_identity()
#     employee_id = identity['employee_id']

#     latest_salary = salary_service.get_latest_salary(employee_id)
#     if not latest_salary:
#         return jsonify({"message": "No salary record found"}), 404

#     # Calculate next payday
#     year, month = map(int, latest_salary['salary_month'].split('-'))
#     today = datetime.now().date()
#     payday = datetime(year, month, 1).replace(day=28) + timedelta(days=4)
#     payday = (payday - timedelta(days=payday.day)).date()  # last day of the month as date

#     days_remaining = (payday - today).days

#     return jsonify({
#         "next_payday": payday.strftime('%Y-%m-%d'),
#         "days_remaining": max(days_remaining, 0),
#         "expected_amount": latest_salary['direct_deposit_amount'],
#         "pay_frequency": latest_salary['pay_frequency']
#     }), 200

from calendar import monthrange

@salary_bp.route('/salary/countdown', methods=['GET'])
@jwt_required()
def salary_countdown():
    identity = get_jwt_identity()
    employee_id = identity['employee_id']

    latest_salary = salary_service.get_latest_salary(employee_id)
    if not latest_salary:
        return jsonify({"message": "No salary record found"}), 404

    today = datetime.now().date()
    year = today.year
    month = today.month

    # Get last day of current month
    last_day = monthrange(year, month)[1]
    payday = date(year, month, last_day)

    days_remaining = (payday - today).days

    return jsonify({
        "next_payday": payday.strftime('%Y-%m-%d'),
        "days_remaining": max(days_remaining, 0),
        "expected_amount": latest_salary['direct_deposit_amount'],
        "pay_frequency": latest_salary['pay_frequency']
    }), 200
