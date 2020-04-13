from flask import render_template, redirect, url_for, request, jsonify
from flask import send_file, send_from_directory, safe_join, abort
from flask_login import current_user, login_user, logout_user, login_required

from app import app, db
from app.forms import LoginForm, RegistrationForm, SystemForm, SystemFormEdit, BuildingForm, FloorForm, CategoryForm, \
    PhaseForm, \
    CompanyFormAdd, CompanyFormEdit, EmployeeFormAdd, EmployeeFormEdit, UserFormEdit, PunchFormEdit, PunchFormAdd, \
    ProjectFormAdd, ProjectFormEdit, ProjectFormSelect, ProjectEmpFormEdit, \
    RequestResetForm, ResetPasswordForm
from app.models import Users, Systems, Buildings, Floors, Categories, Phases, Companies, Employees, Punchlist, \
    Projects_master, Projects_meta

from functools import wraps
import os
import glob
import time
import shutil

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename

# custom imports
from app.xls_export import *
from app.xls_import import *
from app.json_gen import *
from app.pdf_gen import *
from app.dashboard import dashboard_query
from app.graph_gen import index_plot


# FUNCTIONS
# requires_access_level - used to control page access
# allowed_file - used to control allowed estension
#


def requires_access_level(access_level):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.allowed(access_level):
                flash('You do not have access to that page')
                return redirect(url_for('index'))
            return f(*args, **kwargs)

        return decorated_function

    return decorator


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# The following two functions are related to multi project management
#
# prepare_bind
# get_project_session


def prepare_bind(session_project_id):

    data = db.session.query(Projects_master).with_entities(Projects_master.filename).filter(Projects_master.id == str(session_project_id)).first()
    session_db_name = data[0] + '.db'

    if session_project_id not in app.config['SQLALCHEMY_BINDS']:
        app.config['SQLALCHEMY_BINDS'][session_project_id] = 'sqlite:///' + os.path.join(app.config['BASEDIR'], session_db_name)
    return app.config['SQLALCHEMY_BINDS'][session_project_id]


def get_project_session(session_project_id):
    prepare_bind(session_project_id)
    engine = db.get_engine(app, bind=session_project_id)
    session_maker = db.sessionmaker()
    session_maker.configure(bind=engine)
    session = session_maker()
    return session

# send reset email - function to send user email a reset unique link


def send_reset_email(user):
    token = user.get_reset_token()

    # sending reset email
    msg = MIMEMultipart('alternative')
    msg['Subject'] = 'Password Reset'
    msg['From']= app.config['MAIL_USERNAME']
    msg['To'] = user.email

    print(token)

    text = "To reset your password, visit the following link:\nhttp://127.0.0.1:5000/reset_password/" + str(token)

    html = """\
    <html>
    <head></head>
    <body>
    <p>To reset your password, visit the following link:<br>
       <a href="http://127.0.0.1:5000/reset_password/""" + str(token) + """>link</a>
    </p>
    </body>
    </html>
    """

    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')

    msg.attach(part1)
    msg.attach(part2)

    try:
        server = smtplib.SMTP_SSL(app.config['MAILSERVER'], app.config['MAILPORT'])
        server.ehlo()
        server.login(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
        server.sendmail(app.config['MAIL_USERNAME'], user.email, msg.as_string())
        server.close()

        print('Email sent!')
    except:
        print('Something went wrong...')


#
# ROUTES
#

@app.route('/')
@app.route('/index')
@login_required
def index():

    # get project name
    project_name = Projects_master.query.filter_by(id=current_user.get_project()).first()

    # define db project
    data = db.session.query(Projects_master).with_entities(Projects_master.filename).filter(Projects_master.id == str(current_user.get_project())).first()

    # get full path to project db name
    if data:
        session_db_name = data[0] + '.db'
        current_project_db_path = os.path.join(app.config['BASEDIR'], session_db_name)
    else:
        current_project_db_path = os.path.join(app.config['BASEDIR'], 'prologger_000.db')

    master_db_path = os.path.join(app.config['BASEDIR'], 'prologger_master.db')

    if current_user.is_admin() or current_user.is_user():

        # render index page with data
        employee_id = dashboard_query(master_db_path, 0, current_user.get_project(), current_user.id)
        # data_overall is relevant to current project
        data_overall = dashboard_query(current_project_db_path, 1)
        # data_user is relevant to current user
        data_user = dashboard_query(current_project_db_path, 2, current_user.get_project(), employee_id[0])
        # data_system
        data_system = dashboard_query(current_project_db_path,3)
        # generate plot
        index_plot(app.config['IMAGES_FOLDER'], data_overall)

        return render_template('index.html', title='Home', data0=project_name, data1=data_overall, data2=data_user, data3=data_system)

    else:
        return render_template('index.html', title='Home', data0=project_name, data1=None, data2=None, data3=('',''))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()

    # conn = create_connection(app.config['DB_PATH'])
    # cur = conn.cursor()
    # cur.execute("SELECT display FROM employees")
    # rows = cur.fetchall()

    # rows = db.session.query(Employees).with_entities(Employees.display)

    #for row in rows:
    #    form.employee.choices += [(row[0], row[0])]

    if form.validate_on_submit():
        # cur.execute('SELECT id FROM employees WHERE employees.display ="' + form.employee.data + '"')
        # row = cur.fetchone()
        #row = db.session.query(Employees).with_entities(Employees.id).filter_by(display=form.employee.data).first()

        user = Users(username=form.username.data, email=form.email.data, enabled=0, group="users")
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user! Ask your administrator to activate your profile')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()

    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        if not user.is_enabled():
            flash('User is not enabled')
            return redirect(url_for('login'))

        login_user(user, remember=form.remember_me.data)

        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')

        current_project = current_user.get_project()

        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route("/reset_password", methods=['GET','POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RequestResetForm()

    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title='Reset Password', form=form)


@app.route("/reset_password/<token>", methods=['GET','POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    user = Users.verify_reset_token(token)

    if user is None:
        flash('Invalid or expired token')
        return redirect(url_for('reset_request'))

    form = ResetPasswordForm()
    if form.validate_on_submit():

        user.set_password(form.password.data)
        db.session.commit()
        flash('Password changed!')
        return redirect(url_for('login'))

    return render_template('reset_token.html', title='Reset Password', form=form)


@app.route('/projects', methods=['GET', 'POST'])
@requires_access_level('root')
def projects():

    data = db.session.query(Projects_master)
    return render_template('projects.html', title='Projects', data=data)


@app.route('/add_project', methods=['GET', 'POST'])
@requires_access_level('root')
def add_project():

    form = ProjectFormAdd()

    if request.method == 'POST':
        if request.form.get('submit') == 'Add':

            max_id = db.session.query(Projects_master).with_entities(Projects_master.id).order_by(Projects_master.id.desc()).first()
            new_id = max_id[0] + 1
            filename = 'prologger_' + str(new_id).zfill(3)

            day = form.project_start.data[3:5]
            month = form.project_start.data[0:2]
            year = form.project_start.data[6:10]
            start_date = datetime.datetime(int(year), int(month), int(day), 0, 0, 0, 0)

            day = form.project_end.data[3:5]
            month = form.project_end.data[0:2]
            year = form.project_end.data[6:10]
            end_date = datetime.datetime(int(year), int(month), int(day), 0, 0, 0, 0)

            project = Projects_master(filename=filename,
                               number=form.project_number.data,
                               name=form.project_name.data,
                               business=form.project_business.data,
                               region=form.project_region.data,
                               status=form.project_status.data,
                               manager=form.project_manager.data,
                               start_date=start_date,
                               end_date=end_date,
                               address=form.project_address.data,
                               contract_value=form.project_value.data,
                               contract_type=form.project_type.data)

            db.session.add(project)
            db.session.commit()

            dbfile = filename + ".db"
            src = os.path.join(app.config['BASEDIR'],"project_default/prologger_default.db")
            dst = os.path.join(app.config['BASEDIR'],dbfile)

            if os.path.exists(src):
                shutil.copy(src,dst)
            flash('Template db generated for new project ' + form.project_name.data)
            return redirect(url_for('index'))

    return render_template('add_project.html', title='Add a new project', form=form)


@app.route('/project/<int:id>', methods=['GET', 'POST'])
@requires_access_level('root')
def edit_project(id):
    form = ProjectFormEdit()
    qry = db.session.query(Projects_master).filter(Projects_master.id == id)
    project = qry.first()

    if request.method == 'GET':

        if project:

            form.project_name.data = project.__dict__['name']
            form.project_number.data = project.__dict__['number']
            form.project_address.data = project.__dict__['address']
            form.project_business.data = project.__dict__['business']
            form.project_end.data = project.__dict__['end_date']
            form.project_manager.data = project.__dict__['manager']
            form.project_region.data = project.__dict__['region']
            form.project_start.data = project.__dict__['start_date']
            form.project_status.data = project.__dict__['status']
            form.project_type.data = project.__dict__['contract_type']
            form.project_value.data = project.__dict__['contract_value']
            form.project_custom1_name.data = project.__dict__['custom1_name']
            form.project_custom2_name.data = project.__dict__['custom2_name']
            form.project_custom3_name.data = project.__dict__['custom3_name']
            form.project_custom4_name.data = project.__dict__['custom4_name']
            form.project_custom5_name.data = project.__dict__['custom5_name']
            form.project_custom1_sel.data = project.__dict__['custom1_sel']
            form.project_custom2_sel.data = project.__dict__['custom2_sel']
            form.project_custom3_sel.data = project.__dict__['custom3_sel']
            form.project_custom4_sel.data = project.__dict__['custom4_sel']
            form.project_custom5_sel.data = project.__dict__['custom5_sel']

        else:
            return 'Error loading #{id}'.format(id=id)

    elif request.method == 'POST' and request.form.get('submit') == 'Edit':

        project.name = form.project_name.data
        project.number = form.project_number.data
        project.address = form.project_address.data
        project.business = form.project_business.data
        project.manager = form.project_manager.data
        project.region = form.project_region.data
        project.status = form.project_status.data
        project.contract_type = form.project_type.data
        project.contract_value = form.project_value.data
        project.custom1_name = form.project_custom1_name.data
        project.custom2_name = form.project_custom2_name.data
        project.custom3_name = form.project_custom3_name.data
        project.custom4_name = form.project_custom4_name.data
        project.custom5_name = form.project_custom5_name.data
        project.custom1_sel = form.project_custom1_sel.data
        project.custom2_sel = form.project_custom2_sel.data
        project.custom3_sel = form.project_custom3_sel.data
        project.custom4_sel = form.project_custom4_sel.data
        project.custom5_sel = form.project_custom5_sel.data

        if not isinstance(project.start_date, datetime.date):
            day = form.project_start.data[3:5]
            month = form.project_start.data[0:2]
            year = form.project_start.data[6:10]
            project.start_date = datetime.datetime(int(year), int(month), int(day), 0, 0, 0, 0)

        if not isinstance(project.end_date, datetime.date):
            day = form.project_end.data[3:5]
            month = form.project_end.data[0:2]
            year = form.project_end.data[6:10]
            project.end_date = datetime.datetime(int(year), int(month), int(day), 0, 0, 0, 0)

        db.session.commit()
        flash('Project updated successfully!')
        return redirect(url_for('projects'))

    return render_template('edit_project.html', title='Edit Project', form=form)


@app.route('/project_employee/<int:project_id>/<int:user_id>', methods=['GET', 'POST'])
@requires_access_level('root')
def edit_project_employee(project_id,user_id):
    form = ProjectEmpFormEdit()
    qry = db.session.query(Projects_meta).filter((Projects_meta.project_id == project_id) & (Projects_meta.user_allowed == user_id))
    project_employee = qry.first()

    # get project number
    project_session = get_project_session(project_id)

    # connect to session of the same number
    # get employees list
    rows = project_session.query(Employees).with_entities(Employees.display)

    # add choices to select field
    for row in rows:
            form.project_employee.choices += [(row[0], row[0])]

    if request.method == 'GET':

        if project_employee:

            #assign employee name to form var
            qry = db.session.query(Projects_meta).with_entities(Projects_meta.employee_display).filter((Projects_meta.project_id == project_id) & (Projects_meta.user_allowed == user_id))
            employee_display = qry.first()

            if employee_display is not None:
                form.project_employee.data = employee_display[0]

        else:
            return 'Error loading #{id}'.format(id=id)

    elif request.method == 'POST' and request.form.get('submit') == 'Edit':

        qry = project_session.query(Employees).with_entities(Employees.id).filter(Employees.display == form.project_employee.data)
        employee_id = qry.first()

        project_employee.employee_id = employee_id[0]
        project_employee.employee_display = form.project_employee.data

        db.session.commit()
        flash('Project updated successfully!')
        return redirect(url_for('projects'))

    return render_template('edit_project_employee.html', title='Edit Project Employee', form=form)


@app.route('/admin', methods=['GET', 'POST'])
@requires_access_level('root')
def adminpanel():
    data = db.session.query(Users)
    return render_template('adminpanel.html', title='Admin Panel', data=data)


@app.route('/user/<int:id>', methods=['GET', 'POST'])
@requires_access_level('admin')
def edit_user(id):

    form = UserFormEdit()
    qry = db.session.query(Users).filter(Users.id == id)
    edituser = qry.first()

    # Projects list through sqlite3 db call
    conn = create_connection(app.config['MASTER_PATH'])
    cur = conn.cursor()
    cur.execute('SELECT projects_master.id, projects_master.number, projects_master.name, projects_meta.employee_id, projects_meta.user_allowed, projects_meta.employee_display FROM projects_master LEFT OUTER JOIN projects_meta ON projects_master.id = projects_meta.project_id AND projects_meta.user_allowed = ' + str(id) + ' OR projects_meta.user_allowed IS NULL')
    data = cur.fetchall()

    if request.method == 'GET':

        if edituser:

            form.userid.data = edituser.__dict__['id']
            form.username.data = edituser.__dict__['username']
            form.usergroup.data = edituser.__dict__['group']
            form.userenabled.data = edituser.__dict__['enabled']

        else:
            return 'Error loading #{id}'.format(id=id)

    if request.method == 'POST' and request.form.get('submit') == 'Save User':

        edituser.group = form.usergroup.data
        edituser.enabled = form.userenabled.data

        db.session.commit()
        flash('User updated successfully!')
        return redirect(url_for('adminpanel'))

    if request.method == 'POST' and request.form.get('projects') == 'Save Projects':
            projects_ids = request.form.getlist('enabled_id')

            print(projects_ids)

            # check for newly added projects
            for project_id in projects_ids:

                if db.session.query(Projects_meta).filter(Projects_meta.project_id == project_id).filter(Projects_meta.user_allowed == id).first() is None:
                    new_project = Projects_meta(project_id=project_id, user_allowed=id, employee_id=None)
                    db.session.add(new_project)

            # check for deselected projects
            before_edit_projects = db.session.query(Projects_meta).with_entities(Projects_meta.project_id).filter(Projects_meta.user_allowed == id).all()
            user_current_projects=[]

            for el in before_edit_projects:
                user_current_projects.append(str(el[0]))

            for project_id in projects_ids:
                if project_id in user_current_projects:
                    user_current_projects.remove(project_id)

            for el in user_current_projects:
                Projects_meta.query.filter(Projects_meta.project_id == el).delete()

            db.session.commit()

            return redirect(url_for('adminpanel'))

            #refresh view
            #qry = db.session.query(Users).filter(Users.id == id)
            #edituser = qry.first()
            #form.userid.data = edituser.__dict__['id']
            #form.username.data = edituser.__dict__['username']
            #form.usergroup.data = edituser.__dict__['group']
            #form.userenabled.data = edituser.__dict__['enabled']
            #
            #cur.execute('SELECT projects_master.id, projects_master.number, projects_master.name, projects_meta.user_allowed FROM projects_master LEFT OUTER JOIN projects_meta ON projects_master.id = projects_meta.project_id AND projects_meta.user_allowed = ' + str(id) + ' OR projects_meta.user_allowed IS NULL')
            #data = cur.fetchall()
            #return render_template('edit_user.html', form=form, data=data)

    return render_template('edit_user.html', title='Edit User', form=form, data=data)


@app.route('/select_project', methods=['GET', 'POST'])
@requires_access_level('user')
def select_project():

    form = ProjectFormSelect()

    # Projects list through sqlite3 db call
    conn = create_connection(app.config['MASTER_PATH'])
    cur = conn.cursor()
    cur.execute('SELECT projects_master.id, projects_master.number, projects_master.name, projects_meta.user_allowed FROM projects_master INNER JOIN projects_meta ON projects_master.id = projects_meta.project_id AND projects_meta.user_allowed = ' + str(current_user.id))
    data = cur.fetchall()

    if request.method == 'POST':
        if request.form.get('submit') == 'Select':

            # get radio selection from form
            selected_project = request.form['selected_project']

            # set db value for current user
            current_user.set_project(selected_project)
            db.session.commit()

            return redirect(url_for('index'))

    return render_template('select_project.html', title='Select a project', form=form, data=data)


@app.route('/punchlist/<int:view>', methods=['GET', 'POST'])
def punchlist(view):

    data = db.session.query(Projects_master).with_entities(Projects_master.filename).filter(Projects_master.id == str(current_user.get_project())).first()
    session_db_name = data[0] + '.db'

    master_db_path = os.path.join(app.config['BASEDIR'], 'prologger_master.db')
    current_db_path = os.path.join(app.config['BASEDIR'], session_db_name)

    json_gen(master_db_path, current_db_path, view, current_user.username, current_user.id, current_user.get_project(), app.config['JS_PATH'])
    return render_template('punchlist.html', title='Punchlist')


@app.route('/systems', methods=['GET', 'POST'])
@requires_access_level('admin')
def systems():

    project_session = get_project_session(current_user.get_project())

    if not project_session:
        abort(404)
    else:
        if request.method == 'POST':
            if request.form.get('submit1') == 'Add':
                form = SystemForm()
                if form.validate_on_submit():
                    system = Systems(name=form.systemname.data)
                    project_session.add(system)
                    project_session.commit()
                    return redirect(url_for('systems'))
            else:
                delete_ids = request.form.getlist('delete_id')
                for delete_id in delete_ids:
                    project_session.query(Systems).filter(Systems.id == delete_id).delete()
                project_session.commit()

    data = project_session.query(Systems)
    form = SystemForm()
    return render_template('systems.html', title='Systems', form=form, data=data)


@app.route('/edit_system/<int:id>', methods=['GET', 'POST'])
@requires_access_level('admin')
def edit_system(id):

    project_session = get_project_session(current_user.get_project())

    if not project_session:
        abort(404)

    else:

        form = SystemFormEdit()
        qry = project_session.query(Systems).filter(Systems.id == id)
        system = qry.first()

        if request.method == 'GET':

            if system:

                form.systemname.data = system.__dict__['name']

            else:
                return 'Error loading #{id}'.format(id=id)

        elif request.method == 'POST' and form.validate() and request.form.get('submit') == 'Edit':

            system.name = form.systemname.data

            project_session.commit()
            flash('System updated successfully!')
            return redirect(url_for('systems'))

        return render_template('edit_system.html', title='Edit System', form=form)


@app.route('/buildings', methods=['GET', 'POST'])
@requires_access_level('admin')
def buildings():

    project_session = get_project_session(current_user.get_project())

    if not project_session:
        abort(404)
    else:

        if request.method == 'POST':
            if request.form.get('submit1') == 'Add':
                form = BuildingForm()
                if form.validate_on_submit():
                    building = Buildings(name=form.buildingname.data)
                    project_session.add(building)
                    project_session.commit()
                    return redirect(url_for('buildings'))
            else:
                delete_ids = request.form.getlist('delete_id')
                for delete_id in delete_ids:
                    project_session.query(Buildings).filter(Buildings.id == delete_id).delete()
                project_session.commit()

    data = project_session.query(Buildings)
    form = BuildingForm()
    return render_template('buildings.html', title='Buildings', form=form, data=data)


@app.route('/floors', methods=['GET', 'POST'])
@requires_access_level('admin')
def floors():

    project_session = get_project_session(current_user.get_project())

    if not project_session:
        abort(404)
    else:

        if request.method == 'POST':
            if request.form.get('submit1') == 'Add':
                form = FloorForm()
                if form.validate_on_submit():
                    floor = Floors(floor=form.floorname.data)
                    project_session.add(floor)
                    project_session.commit()
                    return redirect(url_for('floors'))
            else:
                delete_ids = request.form.getlist('delete_id')
                for delete_id in delete_ids:
                    project_session.query(Floors).filter(Floors.id == delete_id).delete()
                project_session.commit()

    data = project_session.query(Floors)
    form = FloorForm()
    return render_template('floors.html', title='Floors', form=form, data=data)


@app.route('/categories', methods=['GET', 'POST'])
@requires_access_level('admin')
def categories():

    project_session = get_project_session(current_user.get_project())

    if not project_session:
        abort(404)
    else:
        if request.method == 'POST':
            if request.form.get('submit1') == 'Add':
                form = CategoryForm()
                if form.validate_on_submit():
                    category = Categories(name=form.categoryname.data)
                    project_session.add(category)
                    project_session.commit()
                    return redirect(url_for('categories'))
            else:
                delete_ids = request.form.getlist('delete_id')
                for delete_id in delete_ids:
                    project_session.query(Categories).filter(Categories.id == delete_id).delete()
                project_session.commit()

    data = project_session.query(Categories)
    form = CategoryForm()
    return render_template('categories.html', title='Categories', form=form, data=data)


@app.route('/phases', methods=['GET', 'POST'])
@requires_access_level('admin')
def phases():

    project_session = get_project_session(current_user.get_project())

    if not project_session:
        abort(404)
    else:
        if request.method == 'POST':
            if request.form.get('submit1') == 'Add':
                form = PhaseForm()
                if form.validate_on_submit():
                    phase = Phases(name=form.phasename.data)
                    project_session.add(phase)
                    project_session.commit()
                    return redirect(url_for('phases'))
            else:
                delete_ids = request.form.getlist('delete_id')
                for delete_id in delete_ids:
                    project_session.query(Phases).filter(Phases.id == delete_id).delete()
                project_session.commit()

    data = project_session.query(Phases)
    form = PhaseForm()
    return render_template('phases.html', title='Phases', form=form, data=data)


@app.route('/companies', methods=['GET', 'POST'])
@login_required
def companies():

    project_session = get_project_session(current_user.get_project())

    if not project_session:
        abort(404)

    else:

        data = project_session.query(Companies)
        return render_template('companies.html', title='Companies', data=data)


@app.route('/add_company', methods=['GET', 'POST'])
@requires_access_level('admin')
def add_company():

    project_session = get_project_session(current_user.get_project())

    if not project_session:
        abort(404)

    else:
        form = CompanyFormAdd()
        if request.method == 'POST':
            if request.form.get('submit') == 'Add':
                company = Companies(code=form.companycode.data, name=form.companyname.data, type=form.companytype.data,
                                    address1=form.companyaddress1.data, address2=form.companyaddress2.data,
                                    city=form.companycity.data, country=form.companycountry.data,
                                    division=form.companydivision.data, notes=form.companynotes.data,
                                    email1=form.companyemail1.data, email2=form.companyemail2.data,
                                    sendmail=form.companysendmail.data, frequency=form.companyfrequency.data)
                project_session.add(company)
                project_session.commit()
                return redirect(url_for('companies'))
        return render_template('add_company.html', title='Add New Company', form=form)


@app.route('/company/<int:id>', methods=['GET', 'POST'])
@requires_access_level('admin')
def edit_company(id):

    project_session = get_project_session(current_user.get_project())

    if not project_session:
        abort(404)

    else:

        form = CompanyFormEdit()
        qry = project_session.query(Companies).filter(Companies.id == id)
        company = qry.first()

        if request.method == 'GET':

            if company:

                form.companycode.data = company.__dict__['code']
                form.companyname.data = company.__dict__['name']
                form.companytype.data = company.__dict__['type']
                form.companyaddress1.data = company.__dict__['address1']
                form.companyaddress2.data = company.__dict__['address2']
                form.companycity.data = company.__dict__['city']
                form.companycountry.data = company.__dict__['country']
                form.companydivision.data = company.__dict__['division']
                form.companynotes.data = company.__dict__['notes']
                form.companyemail1.data = company.__dict__['email1']
                form.companyemail2.data = company.__dict__['email2']
                form.companysendmail.data = company.__dict__['sendmail']
                form.companyfrequency.data = company.__dict__['frequency']

            else:
                return 'Error loading #{id}'.format(id=id)

        elif request.method == 'POST' and form.validate() and request.form.get('submit') == 'Edit':

            company.code = form.companycode.data
            company.name = form.companyname.data
            company.type = form.companytype.data
            company.address1 = form.companyaddress1.data
            company.address2 = form.companyaddress2.data
            company.city = form.companycity.data
            company.country = form.companycountry.data
            company.division = form.companydivision.data
            company.notes = form.companynotes.data
            company.email1 = form.companyemail1.data
            company.email2 = form.companyemail2.data
            company.sendmail = form.companysendmail.data
            company.frequency = form.companyfrequency.data

            project_session.commit()
            flash('Company updated successfully!')
            return redirect(url_for('companies'))

        return render_template('edit_company.html', title='Edit Company', form=form)


@app.route('/_parse_employees', methods=['GET'])
def parse_employees():

    project_session = get_project_session(current_user.get_project())

    if not project_session:
        abort(404)

    else:

        if request.method == "GET":
            # only need the id we grabbed in my case.
            id = request.args.get('a', 0)

            # conn = create_connection(app.config['DB_PATH'])
            # cur = conn.cursor()
            # cur.execute('SELECT id from companies WHERE companies.name ="' + str(id) + '"')
            # selected_company = cur.fetchone()

            selected_company = project_session.query(Companies).with_entities(Companies.id).filter(Companies.name == str(id)).first()

            # cur.execute("SELECT display FROM employees WHERE employees.companyid =" + str(selected_company[0]))
            # new_employees_list = cur.fetchall()

            new_employees_tuple = project_session.query(Employees).with_entities(Employees.display).filter(Employees.companyid == str(selected_company[0])).all()
            new_employees_list = []
            for item in new_employees_tuple:
                new_employees_list.append(item[0])
            print(new_employees_list)
            return jsonify(new_employees_list)


@app.route('/employees', methods=['GET', 'POST'])
@login_required
def employees():

    project_session = get_project_session(current_user.get_project())

    if not project_session:
        abort(404)

    else:

        data = project_session.query(Employees.id, Employees.display, Employees.first, Employees.middle, Employees.last,
                                Employees.title, Companies.name).select_from(Employees).join(Companies, Companies.id == Employees.companyid)

        print(data)
        return render_template('employees.html', title='Employees', data=data)


@app.route('/add_employee', methods=['GET', 'POST'])
@requires_access_level('admin')
def add_employee():

    project_session = get_project_session(current_user.get_project())

    if not project_session:
        abort(404)

    else:

        form = EmployeeFormAdd()

        rows = project_session.query(Companies).with_entities(Companies.name)

        for row in rows:
            form.employeecompany.choices += [(row[0], row[0])]

        if request.method == 'POST':
            if request.form.get('submit') == 'Add':

                row = project_session.query(Companies.id).filter(Companies.name == form.employeecompany.data)

                employee = Employees(contactid=form.employeecontactid.data, display=form.employeedisplay.data,
                                     first=form.employeefirst.data,
                                     middle=form.employeemiddle.data, last=form.employeelast.data,
                                     title=form.employeetitle.data, location=form.employeelocation.data,
                                     telephone=form.employeetelephone.data, cell=form.employeecell.data, companyid=row[0][0])
                project_session.add(employee)
                project_session.commit()
                return redirect(url_for('employees'))
        return render_template('add_employee.html', title='Add New Employee', form=form)


@app.route('/employee/<int:id>', methods=['GET', 'POST'])
@requires_access_level('admin')
def edit_employee(id):

    project_session = get_project_session(current_user.get_project())

    if not project_session:
        abort(404)

    else:

        form = EmployeeFormEdit()
        qry = project_session.query(Employees).filter(Employees.id == id)
        employee = qry.first()

        rows = project_session.query(Companies).with_entities(Companies.name)

        for row in rows:
            form.employeecompany.choices += [(row[0], row[0])]

        if request.method == 'GET':

            if employee:


                row = project_session.query(Companies).with_entities(Companies.name).filter_by(id=str(employee.__dict__['companyid'])).first()

                form.employeecontactid.data = employee.__dict__['contactid']
                form.employeedisplay.data = employee.__dict__['display']
                form.employeefirst.data = employee.__dict__['first']
                form.employeemiddle.data = employee.__dict__['middle']
                form.employeelast.data = employee.__dict__['last']
                form.employeetitle.data = employee.__dict__['title']
                form.employeelocation.data = employee.__dict__['location']
                form.employeetelephone.data = employee.__dict__['telephone']
                form.employeecell.data = employee.__dict__['cell']
                form.employeecompany.data = row[0]

            else:
                return 'Error loading #{id}'.format(id=id)

        elif request.method == 'POST' and request.form.get('submit') == 'Edit':

            # cur.execute('SELECT id from companies WHERE companies.name ="' + form.employeecompany.data + '"')
            # row = cur.fetchone()

            row = project_session.query(Companies).with_entities(Companies.id).filter_by(name=form.employeecompany.data).first()

            employee.contactid = form.employeecontactid.data
            employee.display = form.employeedisplay.data
            employee.first = form.employeefirst.data
            employee.middle = form.employeemiddle.data
            employee.last = form.employeelast.data
            employee.title = form.employeetitle.data
            employee.location = form.employeelocation.data
            employee.telephone = form.employeetelephone.data
            employee.cell = form.employeecell.data
            employee.companyid = row[0]

            project_session.commit()
            flash('Employee updated successfully!')
            return redirect(url_for('employees'))

        return render_template('edit_employee.html', title='Edit Employee', form=form)


@app.route('/add_punch', methods=['GET', 'POST'])
@requires_access_level('user')
def add_punch():

    project_session = get_project_session(current_user.get_project())

    if not project_session:
        abort(404)

    else:

        form = PunchFormAdd()

        # Queries to populate SelectFields ###

        rows = project_session.query(Systems).with_entities(Systems.name)
        for row in rows:
            form.punch_system.choices += [(row[0], row[0])]

        rows = project_session.query(Floors).with_entities(Floors.floor)

        for row in rows:
            form.punch_floor.choices += [(row[0], row[0])]

        rows = project_session.query(Categories).with_entities(Categories.name)

        for row in rows:
            form.punch_cat.choices += [(row[0], row[0])]

        rows = project_session.query(Buildings).with_entities(Buildings.name)

        for row in rows:
            form.punch_building.choices += [(row[0], row[0])]

        rows = project_session.query(Phases).with_entities(Phases.name)

        for row in rows:
            form.punch_phase.choices += [(row[0], row[0])]

        rows = project_session.query(Companies).with_entities(Companies.name)

        for row in rows:
            form.punch_closure_c.choices += [(row[0], row[0])]
            form.punch_origin_c.choices += [(row[0], row[0])]
            form.punch_supplier.choices += [(row[0], row[0])]

        if request.method == 'POST':
            if request.form.get('submit') == 'Add':

                row = project_session.query(Employees).with_entities(Employees.id).filter_by(display = form.punch_closure_e.data).first()
                if row:
                    row_closure_e = row[0]
                else:
                    row_closure_e = ""

                row = project_session.query(Systems).with_entities(Systems.id).filter_by(name=form.punch_system.data).first()
                row_system = row[0]

                row = project_session.query(Floors).with_entities(Floors.id).filter_by(floor=form.punch_floor.data).first()
                row_floor = row[0]

                row = project_session.query(Categories).with_entities(Categories.id).filter_by(name=form.punch_cat.data).first()
                row_cat = row[0]

                row = project_session.query(Buildings).with_entities(Buildings.id).filter_by(name=form.punch_building.data).first()
                row_building = row[0]

                row = project_session.query(Phases).with_entities(Phases.id).filter_by(name=form.punch_phase.data).first()
                row_phase = row[0]

                row = project_session.query(Employees).with_entities(Employees.id).filter_by(display=form.punch_origin_e.data).first()
                if row:
                    row_origin_e = row[0]
                else:
                    row_origin_e = ""

                row = project_session.query(Companies).with_entities(Companies.id).filter_by(name = form.punch_supplier.data).first()
                row_supplier = row[0]

                day = form.punch_due_date.data[3:5]
                month = form.punch_due_date.data[0:2]
                year = form.punch_due_date.data[6:10]
                due = datetime.datetime(int(year), int(month), int(day), 0, 0, 0, 0)

                row_closed_by = None

                # set closed_by field if I am closing the field when I am adding it

                if form.punch_status.data:

                    project_number = Projects_master.query.filter_by(id=current_user.get_project()).first()
                    print(project_number)

                    data = db.session.query(Projects_meta).with_entities(Projects_meta.employee_id).filter((Projects_meta.project_id == project_number.id) & (Projects_meta.user_allowed == current_user.id)).first()
                    print(data)

                    row = project_session.query(Employees).with_entities(Employees.display).filter(Employees.id == data[0]).first()

                    print(row)
                    row_closed_by = row[0]

                punchitem = Punchlist(status=form.punch_status.data, discipline=form.punch_discipline.data,
                                      description=form.punch_desc.data,
                                      comments=form.punch_comments.data, date_orig=datetime.datetime.today(),
                                      author_id=row_origin_e, closure_id=row_closure_e,
                                      supplier_id=row_supplier,
                                      system_id=row_system, floor_id=row_floor, cat_id=row_cat,
                                      building_id=row_building, phase_id=row_phase,
                                      due_date=due, closed_by=row_closed_by)

                project_session.add(punchitem)
                project_session.commit()
                return render_template('punchlist.html', title='Punchlist')
        return render_template('add_punch.html', title='Add New Punch Item', form=form)


@app.route('/punchlist/edit/<int:id>', methods=['GET', 'POST'])
@requires_access_level('user')
def edit_punch(id):

    project_session = get_project_session(current_user.get_project())

    if not project_session:
        abort(404)

    else:

        # if item is locked and we are not POSTING
        if os.path.exists(app.config['LOCK_PATH']+str(current_user.get_project())+"/"+str(id)+".lock") and request.method == "GET":
            flash('Punch item is being edited by someone else')
            return redirect("/punchlist/1")

        # else open the punch edit page
        else:

            # if punchitem is not closed
            if project_session.query(Punchlist).with_entities(Punchlist.status).filter(Punchlist.id == id).first()[0] == 0:

                # create lock file in lock directory
                if os.path.exists(app.config['LOCK_PATH']+str(current_user.get_project())):
                    fd = os.open(app.config['LOCK_PATH']+str(current_user.get_project())+"/"+str(id)+".lock", os.O_CREAT)
                else:
                    os.mkdir(app.config['LOCK_PATH']+str(current_user.get_project()))
                    fd = os.open(app.config['LOCK_PATH']+str(current_user.get_project())+"/"+str(id)+".lock", os.O_CREAT)
                os.close(fd)

            form = PunchFormEdit()
            qry = project_session.query(Punchlist).filter(Punchlist.id == id)
            punchitem = qry.first()

            # Queries to populate SelectFields ###

            rows = project_session.query(Systems).with_entities(Systems.name)

            for row in rows:
                form.punch_system.choices += [(row[0], row[0])]

            rows = project_session.query(Floors).with_entities(Floors.floor)

            for row in rows:
                form.punch_floor.choices += [(row[0], row[0])]

            rows = project_session.query(Categories).with_entities(Categories.name)

            for row in rows:
                form.punch_cat.choices += [(row[0], row[0])]

            rows = project_session.query(Buildings).with_entities(Buildings.name)

            for row in rows:
                form.punch_building.choices += [(row[0], row[0])]

            rows = project_session.query(Phases).with_entities(Phases.name)

            for row in rows:
                form.punch_phase.choices += [(row[0], row[0])]

            rows = project_session.query(Companies).with_entities(Companies.name)

            for row in rows:
                form.punch_closure_c.choices += [(row[0], row[0])]
                form.punch_origin_c.choices += [(row[0], row[0])]
                form.punch_supplier.choices += [(row[0], row[0])]

            # Filling Forms Fields

            if request.method == 'GET':

                if punchitem:

                    # closure data

                    closure_id = project_session.query(Employees).with_entities(Employees.display).filter_by(id=str(punchitem.__dict__['closure_id'])).first()

                    closure_company_id = project_session.query(Employees).with_entities(Employees.companyid).filter_by(id=str(punchitem.__dict__['closure_id'])).first()

                    rows = project_session.query(Employees).with_entities(Employees.display).filter_by(companyid=str(closure_company_id[0]))
                    for row in rows:
                        form.punch_closure_e.choices += [(row[0], row[0])]

                    closure_company = project_session.query(Companies).with_entities(Companies.name).filter_by(id=str(closure_company_id[0])).first()

                    # originator data
                    originator_id = project_session.query(Employees).with_entities(Employees.display).filter_by(id=str(punchitem.__dict__['author_id'])).first()

                    originator_company_id = project_session.query(Employees).with_entities(Employees.companyid).filter_by(id=str(punchitem.__dict__['author_id'])).first()

                    rows = project_session.query(Employees).with_entities(Employees.display).filter_by(companyid=str(originator_company_id[0]))
                    for row in rows:
                        form.punch_origin_e.choices += [(row[0], row[0])]

                    originator_company = project_session.query(Companies).with_entities(Companies.id).filter_by(id=str(originator_company_id[0])).first()

                    # other data

                    system_id = project_session.query(Companies).with_entities(Companies.id).filter_by(id=str(originator_company_id[0])).first()
                    floor_id = project_session.query(Floors).with_entities(Floors.floor).filter_by(id=str(punchitem.__dict__['floor_id'])).first()
                    cat_id = project_session.query(Floors).with_entities(Floors.floor).filter_by(id=str(punchitem.__dict__['floor_id'])).first()
                    building_id =  project_session.query(Buildings).with_entities(Buildings.name).filter_by(id=str(punchitem.__dict__['building_id'])).first()
                    phase_id = project_session.query(Phases).with_entities(Phases.name).filter_by(id = str(punchitem.__dict__['phase_id']))
                    supplier_id = project_session.query(Companies).with_entities(Companies.name).filter_by(id = str(punchitem.__dict__['supplier_id']))

                    form.punch_closure_e.data = closure_id[0]
                    form.punch_closure_c.data = closure_company[0]
                    form.punch_origin_e.data = originator_id[0]
                    form.punch_origin_c.data = originator_company[0]
                    form.punch_system.data = system_id[0]
                    form.punch_floor.data = floor_id[0]
                    form.punch_cat.data = cat_id[0]
                    form.punch_building.data = building_id[0]
                    form.punch_phase.data = phase_id[0]
                    form.punch_supplier.data = supplier_id[0]
                    form.punch_id.data = punchitem.__dict__['id']
                    form.punch_status.data = punchitem.__dict__['status']
                    form.punch_closed_by.data = punchitem.__dict__['closed_by']
                    form.punch_desc.data = punchitem.__dict__['description']
                    form.punch_comments.data = punchitem.__dict__['comments']
                    form.punch_orig_date.data = punchitem.__dict__['date_orig']
                    form.punch_due_date.data = punchitem.__dict__['due_date']
                    form.punch_discipline.data = punchitem.__dict__['discipline']

                    # create attachment list to be used into the modal view

                    att_path = app.config['REPO_FOLDER'] + str(id) + "/"

                    file_list = []
                    for root, dirs, files in os.walk(att_path, topdown=False):
                            for f in files:
                                if '.txt' or '.csv' or '.xls' or '.doc' or '.docx' or '.pdf' or '.jpg' or '.png' in f:
                                    file_list.append([f,'repository/'+str(id)+'/'+f])
                    att_list = file_list

                else:
                    return 'Error loading #{id}'.format(id=id)

            elif request.method == 'POST' and request.form.get('submit') == 'Edit':

                row = project_session.query(Employees).with_entities(Employees.id).filter_by(display = form.punch_closure_e.data).first()
                punchitem.closure_id = row[0]

                punchitem.status = form.punch_status.data

                row = project_session.query(Systems).with_entities(Systems.id).filter_by(name = form.punch_system.data).first()
                punchitem.system_id = row[0]

                row = project_session.query(Floors).with_entities(Floors.id).filter_by(floor = form.punch_floor.data).first()
                punchitem.floor_id = row[0]

                row = project_session.query(Categories).with_entities(Categories.id).filter_by(name = form.punch_cat.data).first()
                punchitem.cat_id = row[0]

                row = project_session.query(Buildings).with_entities(Buildings.id).filter_by(name = form.punch_building.data).first()
                punchitem.building_id = row[0]

                row = project_session.query(Phases).with_entities(Phases.id).filter_by(name = form.punch_phase.data).first()
                punchitem.phase_id = row[0]

                row = project_session.query(Employees).with_entities(Employees.id).filter_by(display = form.punch_origin_e.data).first()
                punchitem.author_id = row[0]

                row = project_session.query(Companies).with_entities(Companies.id).filter_by(name = form.punch_supplier.data).first()
                punchitem.supplier_id = row[0]

                punchitem.discipline = form.punch_discipline.data
                punchitem.description = form.punch_desc.data
                punchitem.comments = form.punch_comments.data

                # calculate due date in datetime format

                if not isinstance(punchitem.due_date, datetime.date):
                    day = form.punch_due_date.data[3:5]
                    month = form.punch_due_date.data[0:2]
                    year = form.punch_due_date.data[6:10]
                    due = datetime.datetime(int(year), int(month), int(day), 0, 0, 0, 0)

                    punchitem.due_date = due

                if punchitem.status:

                    row = project_session.query(Employees).with_entities(Employees.display).filter_by(id = str(current_user.employee())).first()
                    punchitem.closed_by = row[0]

                project_session.commit()
                flash('Punch item updated successfully!')

                # remove lock file
                os.remove(app.config['LOCK_PATH']+str(id)+".lock")

                time.sleep(3)
                return redirect("/punchlist/1")

        return render_template('edit_punch.html', title='Edit Punch Item', form=form, att_data=att_list)


@app.route('/about', methods=['GET'])
def about():
    return render_template('about.html', title='About')


@app.route('/files', methods=['GET', 'POST'])
@requires_access_level('admin')
def files():

    # define db project
    data = db.session.query(Projects_master).with_entities(Projects_master.filename).filter(Projects_master.id == str(current_user.get_project())).first()
    session_db_name = data[0] + '.db'

    # get full path to db name
    current_db_path = os.path.join(app.config['BASEDIR'], session_db_name)

    if request.method == 'POST' and request.form.get('submit1') == 'Import Punchlist':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No file selected for uploading')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['IMPORT_FOLDER'], filename))
            flash('File(s) successfully uploaded')

            punchlist_import(current_db_path, os.path.join(app.config['IMPORT_FOLDER'], filename),
                             app.config['LOG_FOLDER'])
            return redirect(url_for('files'))

    elif request.method == 'POST' and request.form.get('submit2') == 'Export Punchlist':

        # assign query var
        sqlfile = open(app.config['QUERIES_FOLDER'] + 'punchlist.sql', "r")
        if sqlfile.mode == 'r':
            query = sqlfile.read()

        punchlist_export(current_db_path, app.config['EXPORT_FOLDER'], app.config['IMAGES_FOLDER'],
                         query)

        try:
            return send_from_directory(app.config["EXPORT_FOLDER"], filename='Prologger_Export.xlsx',
                                       as_attachment=True)
        except FileNotFoundError:
            abort(404)

    elif request.method == 'POST' and request.form.get('submit3') == 'Export Punchlist Template':
        punchlist_template_export(current_db_path, app.config['EXPORT_FOLDER'])

        try:
            return send_from_directory(app.config["EXPORT_FOLDER"], filename='Prologger_Template.xlsx',
                                       as_attachment=True)
        except FileNotFoundError:
            abort(404)

    elif request.method == 'POST' and request.form.get('submit5') == 'Import Systems':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No file selected for uploading')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['IMPORT_FOLDER'], filename))
            flash('File(s) successfully uploaded')

            systems_import(current_db_path,os.path.join(app.config['IMPORT_FOLDER'], filename))
            return redirect(url_for('files'))

    return render_template('files.html', title='Files Import / Export')


@app.route('/utils', methods=['GET', 'POST'])
@requires_access_level('admin')
def utils():

    if request.method == 'POST' and request.form.get('release_locks') == 'Release All Locks':


        folder = app.config['LOCK_PATH']
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))

        flash('Locks Released!')
        return redirect(url_for('utils'))


    else:
        return render_template('utils.html', title='Utils')


@app.route('/upload/<int:id>', methods=['GET', 'POST'])
@requires_access_level('user')
def upload(id):

    # check if dir id exists and if not create it
    if os.path.exists(app.config['REPO_FOLDER'] + str(id)):
        print('upload dir exists')
        if request.method == 'POST' and request.form.get('submit1') == 'Upload attachment':
            if 'file' not in request.files:
                flash('No file part')
                return redirect(request.url)
            file = request.files['file']
            if file.filename == '':
                flash('No file selected for uploading')
                return redirect(request.url)
            if file and os.path.exists(app.config['REPO_FOLDER']+str(id)+'/'+file.filename):
                flash('File already exists')
                return redirect(request.url)
            else:
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['REPO_FOLDER'] + str(id), filename))
                flash('File ' + filename + ' successfully uploaded')

    else:
        try:
            print(app.config['REPO_FOLDER'])
            os.mkdir(app.config['REPO_FOLDER'] + str(id))
        except OSError:
            print ("Creation of the upload directory for punch item failed" )
        else:
            print ("Successfully created the upload directory for punch item")
            if request.method == 'POST' and request.form.get('submit1') == 'Upload Attachment':
                if 'file' not in request.files:
                    flash('No file part')
                    return redirect(request.url)
                file = request.files['file']
                if file.filename == '':
                    flash('No file selected for uploading')
                    return redirect(request.url)
                if file:
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(app.config['REPO_FOLDER'] + str(id), filename))
                    flash('File(s) successfully uploaded')

    # upload the file
    return render_template('upload.html', title='Upload Attachment')


@app.route('/pdf_report', methods=['GET'])
@requires_access_level('user')
def pdf_report():

    try:
        print('pdf_report triggered')
        # before generating the pdf, define db session and db name
        data = db.session.query(Projects_master).with_entities(Projects_master.filename).filter(Projects_master.id == str(current_user.get_project())).first()
        session_db_name = data[0] + '.db'

        # get full path to db name
        master_db_path = os.path.join(app.config['BASEDIR'],'prologger_master.db')
        current_db_path = os.path.join(app.config['BASEDIR'], session_db_name)

        # generate json file
        json_gen(master_db_path, current_db_path, 1, current_user.username, current_user.id, current_user.get_project(), app.config['JS_PATH'])

        # build json dump file
        json_dump = app.config["JS_PATH"] + "datatable_" + current_user.username + ".ajax"

        # call create_report function
        report_file = create_report(app.config['REPORT_FOLDER'], json_dump)

        # return file from browser
        return send_from_directory(app.config["REPORT_FOLDER"], report_file, as_attachment=True, cache_timeout=0)

    except FileNotFoundError:
        abort(404)

#
# ROUTES END
#
