import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'employees.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
ma = Marshmallow(app)

class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(15), nullable=False)
    location = db.Column(db.String(200), nullable=False)
    company_name = db.Column(db.String(100), nullable=False)
    profile_image = db.Column(db.String(200))
    slide_image = db.Column(db.String(200))

class EmployeeSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Employee
        load_instance = True

employee_schema = EmployeeSchema()
employees_schema = EmployeeSchema(many=True)

@app.route("/employee", methods=["POST"])
def add_employee():
    name = request.form.get('name')
    phone_number = request.form.get('phone_number')
    location = request.form.get('location')
    company_name = request.form.get('company_name')

    profile_image_file = request.files.get('profile_image')
    slide_image_file = request.files.get('slide_image')

    upload_folder = os.path.join(basedir, "uploads")
    os.makedirs(upload_folder, exist_ok=True)

    profile_image_path = None
    slide_image_path = None

    if profile_image_file:
        profile_image_path = os.path.join(upload_folder, profile_image_file.filename)
        profile_image_file.save(profile_image_path)

    if slide_image_file:
        slide_image_path = os.path.join(upload_folder, slide_image_file.filename)
        slide_image_file.save(slide_image_path)

    new_employee = Employee(
        name=name,
        phone_number=phone_number,
        location=location,
        company_name=company_name,
        profile_image=profile_image_path,
        slide_image=slide_image_path
    )
    db.session.add(new_employee)
    db.session.commit()

    return employee_schema.jsonify(new_employee)

@app.route("/allData", methods=["GET"])
def get_employees():
    all_employees = Employee.query.all()
    return employees_schema.jsonify(all_employees)

# IMPORTANT: Do not run app.run()
def handler(request, response):
    return app(request, response)
