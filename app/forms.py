from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, SelectMultipleField, widgets, RadioField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, Optional
from app.models import Users


class MultiCheckboxField(SelectMultipleField):
    """
    A multiple-select, except displays a list of checkboxes.

    Iterating the field will produce subfields, allowing custom rendering of
    the enclosed checkbox fields.
    """
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    # employee = SelectField(u'Employee', choices=[])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = Users.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = Users.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')


class RequestResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request')

    def validate_email(self, email):
        user = Users.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('No account for this email.')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Confirm new password')


class SystemForm(FlaskForm):

    systemname = StringField('System', validators=[DataRequired()])
    submit1 = SubmitField('Add')


class SystemFormEdit(FlaskForm):

    systemname = StringField('System', validators=[DataRequired()])
    submit1 = SubmitField('Add')


class BuildingForm(FlaskForm):

    buildingname = StringField('Building', validators=[DataRequired()])
    submit1 = SubmitField('Add')


class FloorForm(FlaskForm):

    floorname = StringField('Floor', validators=[DataRequired()])
    submit1 = SubmitField('Add')


class CategoryForm(FlaskForm):

    categoryname = StringField('Category', validators=[DataRequired()])
    submit1 = SubmitField('Add')


class PhaseForm(FlaskForm):

    phasename = StringField('Phase', validators=[DataRequired()])
    submit1 = SubmitField('Add')


class CompanyFormAdd(FlaskForm):
    companycode = StringField('Code', validators=[DataRequired()])
    companyname = StringField('Name', validators=[DataRequired()])
    companytype = SelectField(u'Type', choices=[('Construction Manager','Construction Manager'),('Engineer','Engineer'),('Owner','Owner'),('Contractor','Contractor'),('Subcontractor','Subcontractor'),('Vendor','Vendor')])
    companyaddress1 = StringField('Address1', validators=[DataRequired()])
    companyaddress2 = StringField('Address2')
    companycity = StringField('City', validators=[DataRequired()])
    companycountry = StringField('Country', validators=[DataRequired()])
    companydivision = StringField('Division')
    companynotes = StringField('Notes', widget=widgets.TextArea())
    companyemail1 = StringField('Email 1', validators=[Email()])
    companyemail2 = StringField('Email 2', validators=[Email()])
    companysendmail = BooleanField('Email Open Items Automatically')
    companyfrequency = SelectField(u'Frequency', choices=[('Hourly', 'Hourly'), ('Daily', 'Daily'), ('Weekly', 'Weekly')])
    submit = SubmitField('Add')


class CompanyFormEdit(FlaskForm):
    companycode = StringField('Code', validators=[DataRequired()])
    companyname = StringField('Name', validators=[DataRequired()])
    companytype = SelectField(u'Type', choices=[('Construction Manager','Construction Manager'),('Engineer','Engineer'),('Owner','Owner'),('Contractor','Contractor'),('Subcontractor','Subcontractor'),('Vendor','Vendor')])
    companyaddress1 = StringField('Address1', validators=[DataRequired()])
    companyaddress2 = StringField('Address2')
    companycity = StringField('City', validators=[DataRequired()])
    companycountry = StringField('Country', validators=[DataRequired()])
    companydivision = StringField('Division')
    companynotes = StringField('Notes', widget=widgets.TextArea())
    companyemail1 = StringField('Email 1', validators=[Email(), Optional()])
    companyemail2 = StringField('Email 2', validators=[Email(), Optional()])
    companysendmail = BooleanField('Email Open Items Automatically')
    companyfrequency = SelectField(u'Frequency', choices=[('Hourly', 'Hourly'), ('Daily', 'Daily'), ('Weekly', 'Weekly')])
    submit = SubmitField('Edit')


class EmployeeFormAdd(FlaskForm):
    employeecontactid = StringField('Contact Id', validators=[DataRequired()])
    employeedisplay = StringField('Display Name', validators=[DataRequired()])
    employeefirst = StringField('First Name', validators=[DataRequired()])
    employeemiddle = StringField('Middle Name')
    employeelast = StringField('Last Name', validators=[DataRequired()])
    employeetitle = StringField('Title')
    employeelocation = StringField('Location')
    employeetelephone = StringField('Telephone')
    employeecell = StringField('Cell')
    employeecompany = SelectField(u'Company', choices=[])
    submit = SubmitField('Add')


class EmployeeFormEdit(FlaskForm):
    employeecontactid = StringField('Contact Id', validators=[DataRequired()])
    employeedisplay = StringField('Display Name', validators=[DataRequired()])
    employeefirst = StringField('First Name', validators=[DataRequired()])
    employeemiddle = StringField('Middle Name')
    employeelast = StringField('Last Name', validators=[DataRequired()])
    employeetitle = StringField('Title')
    employeelocation = StringField('Location')
    employeetelephone = StringField('Telephone')
    employeecell = StringField('Cell')
    employeecompany = SelectField(u'Company', choices=[])
    submit = SubmitField('Edit')


class UserFormEdit(FlaskForm):
    userid = StringField('Id')
    username = StringField('User name')
    usergroup = SelectField(u'Group', choices=[('users','users'),('admin','admin'),('root','root')])
    userenabled = BooleanField('Enabled')
    submit = SubmitField('Save')


class PunchFormEdit(FlaskForm):
    punch_id = StringField('Id', render_kw={'readonly': True})
    punch_closure_c = SelectField('Closure Company', choices=[])
    punch_closure_e = SelectField('Closure Employee', choices=[])
    punch_status = BooleanField('Closed')
    punch_system = SelectField(u'System', choices=[])
    punch_floor = SelectField(u'Floor', choices=[])
    punch_cat = SelectField(u'Category', choices=[])
    punch_building = SelectField(u'Building', choices=[])
    punch_phase = SelectField(u'Phase', choices=[])
    punch_origin_c = SelectField('Originator Company', choices=[])
    punch_origin_e = SelectField('Originator Employee', choices=[])
    punch_supplier = SelectField('Supplier', choices=[])
    punch_closed_by = StringField('Closed By')
    punch_desc = StringField('Description', widget=widgets.TextArea())
    punch_comments = StringField('Comments', widget=widgets.TextArea())
    punch_orig_date = StringField('Originated', render_kw={'readonly': True})
    punch_due_date = StringField('Due')
    punch_custom1 = StringField('Custom 1')
    punch_custom2 = StringField('Custom 2')
    punch_custom3 = StringField('Custom 3')
    punch_custom4 = StringField('Custom 4')
    punch_custom5 = StringField('Custom 5')
    punch_discipline = SelectField(u'Discipline', choices=[('HVAC', 'HVAC'), ('Civil', 'Civil'),
                                                        ('Electrical', 'Electrical'),
                                                        ('Automation', 'Automation'), ('Safety', 'Safety'),
                                                        ('Equipment', 'Equipment')])
    submit = SubmitField('Edit')


class PunchFormAdd(FlaskForm):
    punch_id = StringField('Id', render_kw={'readonly': True})
    punch_closure_c = SelectField('Closure Company', choices=[])
    punch_closure_e = SelectField('Closure Employee', choices=[])
    punch_status = BooleanField('Closed')
    punch_system = SelectField(u'System', choices=[])
    punch_floor = SelectField(u'Floor', choices=[])
    punch_cat = SelectField(u'Category', choices=[])
    punch_building = SelectField(u'Building', choices=[])
    punch_phase = SelectField(u'Phase', choices=[])
    punch_origin_c = SelectField('Originator Company', choices=[])
    punch_origin_e = SelectField('Originator Employee', choices=[], validators=[DataRequired()])
    punch_supplier = SelectField('Supplier', choices=[])
    punch_closed_by = StringField('Closed By')
    punch_desc = StringField('Description', widget=widgets.TextArea())
    punch_comments = StringField('Comments', widget=widgets.TextArea())
    punch_orig_date = StringField('Originated', render_kw={'readonly': True})
    punch_due_date = StringField('Due')
    punch_custom1 = StringField('Custom 1')
    punch_custom2 = StringField('Custom 2')
    punch_custom3 = StringField('Custom 3')
    punch_custom4 = StringField('Custom 4')
    punch_custom5 = StringField('Custom 5')
    punch_discipline = SelectField('Discipline', choices=[('HVAC', 'HVAC'), ('Civil', 'Civil'),
                                                        ('Electrical', 'Electrical'),
                                                        ('Automation', 'Automation'), ('Safety', 'Safety'),
                                                        ('Equipment', 'Equipment')])
    submit = SubmitField('Add')


class ProjectFormEdit(FlaskForm):
    project_number = StringField('Project No.')
    project_name = StringField('Project Name')
    project_business = SelectField('Business', choices=[('Buildings', 'Buildings'),('Pharma', 'Pharma'),
                                                        ('Chemical', 'Chemical'),
                                                        ('Oil&Gas', 'Oil&Gas'), ('Environmental', 'Environmental'),
                                                        ('Data','Data'), ('Civil','Civil')])
    project_region = SelectField('Region', choices=[('North Europe','North Europe'), ('South Europe','South Europe'),
                                                    ('North America','North America'),
                                                    ('South America','South America')])
    project_status = SelectField('Status', choices=[('In progress','In progress'),('Completed','Completed'),('Aborted','Aborted')])
    project_manager = StringField('Project Manager')
    project_start = StringField('Project Start')
    project_end = StringField('Project End')
    project_value = StringField('Project Value')
    project_type = SelectField(u'Type', choices=[('Lump Sum','Lump Sum'), ('Time&Material','Time&Material')])
    project_address = StringField('Address', widget=widgets.TextArea())
    project_custom1_name = StringField('Custom Field 1',validators=[Optional()])
    project_custom2_name = StringField('Custom Field 2',validators=[Optional()])
    project_custom3_name = StringField('Custom Field 3',validators=[Optional()])
    project_custom4_name = StringField('Custom Field 4',validators=[Optional()])
    project_custom5_name = StringField('Custom Field 5',validators=[Optional()])
    project_custom1_sel = BooleanField(validators=[Optional()])
    project_custom2_sel = BooleanField(validators=[Optional()])
    project_custom3_sel = BooleanField(validators=[Optional()])
    project_custom4_sel = BooleanField(validators=[Optional()])
    project_custom5_sel = BooleanField(validators=[Optional()])
    submit = SubmitField('Edit')


class ProjectFormAdd(FlaskForm):
    project_number = StringField('Project No.')
    project_name = StringField('Project Name')
    project_business = SelectField('Business', choices=[('Buildings', 'Buildings'),('Pharma', 'Pharma'),
                                                        ('Chemical', 'Chemical'),
                                                        ('Oil&Gas', 'Oil&Gas'), ('Environmental', 'Environmental'),
                                                        ('Data','Data'), ('Civil','Civil')])
    project_region = SelectField('Region', choices=[('North Europe','North Europe'), ('South Europe','South Europe'),
                                                    ('North America','North America'),
                                                    ('South America','South America')])
    project_status = SelectField('Status', choices=[('In progress','In progress'),('Completed','Completed'),('Aborted','Aborted')])
    project_manager = StringField('Project Manager')
    project_start = StringField('Project Start')
    project_end = StringField('Project End')
    project_value = StringField('Project Value')
    project_type = SelectField(u'Type', choices=[('Lump Sum','Lump Sum'), ('Time&Material','Time&Material')])
    project_address = StringField('Address', widget=widgets.TextArea())
    project_custom1_name = StringField('Custom Field 1',validators=[Optional()])
    project_custom2_name = StringField('Custom Field 2',validators=[Optional()])
    project_custom3_name = StringField('Custom Field 3',validators=[Optional()])
    project_custom4_name = StringField('Custom Field 4',validators=[Optional()])
    project_custom5_name = StringField('Custom Field 5',validators=[Optional()])
    project_custom1_sel = BooleanField(validators=[Optional()])
    project_custom2_sel = BooleanField(validators=[Optional()])
    project_custom3_sel = BooleanField(validators=[Optional()])
    project_custom4_sel = BooleanField(validators=[Optional()])
    project_custom5_sel = BooleanField(validators=[Optional()])
    submit = SubmitField('Add')


class ProjectFormSelect(FlaskForm):
    project = RadioField('Project', choices=[])


class ProjectEmpFormEdit(FlaskForm):
    project_employee = SelectField(u'Employee Name', choices=[])
    submit = SubmitField('Edit')