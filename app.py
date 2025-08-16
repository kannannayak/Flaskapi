"""from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)

# Database Config (MySQL)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/company_db'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://username:password@localhost/dbname'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:YOUR_PASSWORD@localhost:3306/employees_db'


app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Upload Config
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Init Extensions
db = SQLAlchemy(app)
ma = Marshmallow(app)

# Model
class Employee(db.Model):
    __tablename__ = 'employees'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    company_name = db.Column(db.String(100), nullable=False)
    profile_image = db.Column(db.String(255))
    slide_images = db.Column(db.Text)  # Comma-separated paths

# Schema
class EmployeeSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Employee
        load_instance = True

employee_schema = EmployeeSchema()
employees_schema = EmployeeSchema(many=True)

# Create table (only first time)
with app.app_context():
    db.create_all()

# Helper
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# POST API
@app.route('/add_employee', methods=['POST'])
def add_employee():
    required_fields = ['name', 'phone_number', 'location', 'company_name']
    for field in required_fields:
        if not request.form.get(field):
            return jsonify({"message": f"{field} is required"}), 400

    # Profile image
    profile_image_path = None
    profile_image_file = request.files.get('profile_image')
    if profile_image_file and allowed_file(profile_image_file.filename):
        filename = secure_filename(profile_image_file.filename)
        profile_image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        profile_image_file.save(profile_image_path)

    # Slide images
    slide_image_files = request.files.getlist('slide_images')
    slide_image_paths = []
    for img in slide_image_files:
        if img and allowed_file(img.filename):
            filename = secure_filename(img.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            img.save(file_path)
            slide_image_paths.append(file_path)

    # Save to DB
    new_employee = Employee(
        name=request.form.get('name'),
        phone_number=request.form.get('phone_number'),
        location=request.form.get('location'),
        company_name=request.form.get('company_name'),
        profile_image=profile_image_path,
        slide_images=",".join(slide_image_paths)
    )
    db.session.add(new_employee)
    db.session.commit()

    return jsonify({
        "message": "Employee added successfully",
        "employee": employee_schema.dump(new_employee)
    }), 201

# GET all
@app.route('/employees', methods=['GET'])
def get_employees():
    all_employees = Employee.query.all()
    return jsonify({
        "employees": employees_schema.dump(all_employees)
    })

# GET by ID
@app.route('/employee/<int:id>', methods=['GET'])
def get_employee(id):
    employee = Employee.query.get(id)
    if not employee:
        return jsonify({"message": "Employee not found"}), 404
    return jsonify({
        "employee": employee_schema.dump(employee)
    })

if __name__ == '__main__':
    app.run(debug=True)
"""




import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

# Get base directory path
basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

# Database configuration (SQLite by default)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'employees.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database & marshmallow
db = SQLAlchemy(app)
ma = Marshmallow(app)

# Employee model
class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(15), nullable=False)
    location = db.Column(db.String(200), nullable=False)
    company_name = db.Column(db.String(100), nullable=False)
    profile_image = db.Column(db.String(200))
    slide_image = db.Column(db.String(200))

    def __init__(self, name, phone_number, location, company_name, profile_image=None, slide_image=None):
        self.name = name
        self.phone_number = phone_number
        self.location = location
        self.company_name = company_name
        self.profile_image = profile_image
        self.slide_image = slide_image

# Employee schema
class EmployeeSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Employee
        load_instance = True

employee_schema = EmployeeSchema()
employees_schema = EmployeeSchema(many=True)

# Create employee API
@app.route("/employee", methods=["POST"])
def add_employee():
    name = request.form.get('name')
    phone_number = request.form.get('phone_number')
    location = request.form.get('location')
    company_name = request.form.get('company_name')

    # File uploads
    profile_image_file = request.files.get('profile_image')
    slide_image_file = request.files.get('slide_image')

    profile_image_path = None
    slide_image_path = None

    upload_folder = os.path.join(basedir, "uploads")
    os.makedirs(upload_folder, exist_ok=True)

    if profile_image_file:
        profile_image_path = os.path.join(upload_folder, profile_image_file.filename)
        profile_image_file.save(profile_image_path)

    if slide_image_file:
        slide_image_path = os.path.join(upload_folder, slide_image_file.filename)
        slide_image_file.save(slide_image_path)

    new_employee = Employee(name, phone_number, location, company_name, profile_image_path, slide_image_path)
    db.session.add(new_employee)
    db.session.commit()

    return employee_schema.jsonify(new_employee)

# Get all employees
@app.route("/allData", methods=["GET"])
def get_employees():
    all_employees = Employee.query.all()
    return employees_schema.jsonify(all_employees)

# Run app
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
       # app.run(debug=True)
        
  