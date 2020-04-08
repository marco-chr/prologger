from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

class Users(UserMixin, db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password = db.Column(db.String(128))
    enabled = db.Column(db.Boolean)
    group = db.Column(db.String(15))
    employeeid = db.Column(db.Integer, db.ForeignKey('employees.id'))
    project = db.Column(db.Integer)

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self,password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def is_enabled(self):
        return self.enabled

    def get_reset_token(self, expires_sec=1800):
        s = Serializer('90125', expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer('90125')
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None

        return Users.query.get(user_id)

    def is_user(self):
        return self.group == 'users'

    def is_root(self):
        return self.group == 'root'

    def is_admin(self):
        return self.group == 'admin'

    def allowed(self, access_level):
        if access_level == 'admin' and (self.group == 'admin' or self.group == 'root'):
            return True
        elif access_level == 'root' and (self.group == 'root'):
            return True
        elif access_level == 'user':
            return True
        else:
            return False

    def employee(self):
        return self.employeeid

    def set_project(self,project):
        self.project = project

    def get_project(self):
        return self.project

@login.user_loader
def load_user(id):
    return Users.query.get(int(id))

class Punchlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.Boolean)
    discipline = db.Column(db.String(64), index=True)
    description = db.Column(db.String(255), index=True)
    comments = db.Column(db.String(255), index=True)
    date_orig = db.Column(db.DateTime, index=True)
    due_date = db.Column(db.DateTime, index=True)
    author_id = db.Column(db.Integer, db.ForeignKey('employees.id'))
    closure_id = db.Column(db.Integer, db.ForeignKey('employees.id'))
    supplier_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    system_id = db.Column(db.Integer, db.ForeignKey('systems.id'))
    floor_id = db.Column(db.Integer, db.ForeignKey('floors.id'))
    phase_id = db.Column(db.Integer, db.ForeignKey('phases.id'))
    cat_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    building_id = db.Column(db.Integer, db.ForeignKey('buildings.id'))
    closed_by = db.Column(db.Integer, db.ForeignKey('employees.id'))
    custom1 = db.Column(db.String(128), index=True)
    custom2 = db.Column(db.String(128), index=True)
    custom3 = db.Column(db.String(128), index=True)
    custom4 = db.Column(db.String(128), index=True)
    custom5 = db.Column(db.String(128), index=True)

class Systems(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), index=True)

class Buildings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(15), index=True)

class Floors(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    floor = db.Column(db.String(25), index=True)

class Categories(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(10), index=True)

class Phases(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(25), index=True)

class Companies(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(10), index=True)
    name = db.Column(db.String(50), index=True)
    type = db.Column(db.String(25), index=True)
    address1 = db.Column(db.String(25), index=True)
    address2 = db.Column(db.String(25), index=True)
    city = db.Column(db.String(25), index=True)
    country = db.Column(db.String(25), index=True)
    division = db.Column(db.String(25), index=True)
    notes = db.Column(db.String(25), index=True)
    email1 = db.Column(db.String(50), index=True)
    email2 = db.Column(db.String(50), index=True)
    sendmail = db.Column(db.Boolean)
    frequency = db.Column(db.String(25), index=True)

class Employees(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    contactid = db.Column(db.String(8), index=True)
    display = db.Column(db.String(62), index=True)
    first = db.Column(db.String(20), index=True)
    middle = db.Column(db.String(20), index=True)
    last = db.Column(db.String(20), index=True)
    title = db.Column(db.String(20), index=True)
    location = db.Column(db.String(20), index=True)
    telephone = db.Column(db.String(20), index=True)
    cell = db.Column(db.String(20), index=True)
    companyid = db.Column(db.Integer, index=True)

class Projects_master(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(15), index=True)
    number = db.Column(db.String(72), index=True)
    name = db.Column(db.String(72), index=True)
    business = db.Column(db.String(72), index=True)
    region = db.Column(db.String(72), index=True)
    status = db.Column(db.Boolean)
    manager = db.Column(db.String(72), index=True)
    start_date = db.Column(db.DateTime, index=True)
    end_date = db.Column(db.DateTime, index=True)
    address = db.Column(db.String(255), index=True)
    contract_value = db.Column(db.Integer, index=True)
    contract_type = db.Column(db.String(72), index=True)
    custom1_name = db.Column(db.String(72), index=True)
    custom2_name = db.Column(db.String(72), index=True)
    custom3_name = db.Column(db.String(72), index=True)
    custom4_name = db.Column(db.String(72), index=True)
    custom5_name = db.Column(db.String(72), index=True)
    custom1_sel = db.Column(db.Boolean)
    custom2_sel = db.Column(db.Boolean)
    custom3_sel = db.Column(db.Boolean)
    custom4_sel = db.Column(db.Boolean)
    custom5_sel = db.Column(db.Boolean)

class Projects_meta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects_master.id'))
    user_allowed = db.Column(db.Integer, db.ForeignKey('users.id'))
    employee_id = db.Column(db.Integer)
    employee_display = db.Column(db.String(62), index=True)