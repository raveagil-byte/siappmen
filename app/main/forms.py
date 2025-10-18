from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, IntegerField, TextAreaField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError
from app.models import User, Unit, Instrument

class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

class LoginForm(FlaskForm):
    username = StringField('Username',
                        validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class LoanForm(FlaskForm):
    unit_id = SelectField('Unit', coerce=int, validators=[DataRequired()])
    instrument_id = SelectField('Instrument', coerce=int, validators=[DataRequired()])
    patient_name = StringField('Patient Name')
    notes = TextAreaField('Notes')
    submit = SubmitField('Create Loan')

    def __init__(self, *args, **kwargs):
        super(LoanForm, self).__init__(*args, **kwargs)
        self.unit_id.choices = [(u.id, u.name) for u in Unit.query.order_by('name').all()]
        self.instrument_id.choices = [(i.id, i.name) for i in Instrument.query.filter_by(status='available').order_by('name').all()]

class ReturnForm(FlaskForm):
    qr_code = StringField('QR Code', validators=[DataRequired()])
    completeness_status = SelectField('Completeness Status',
                                      choices=[('complete', 'Complete'),
                                               ('incomplete', 'Incomplete'),
                                               ('damaged', 'Damaged')],
                                      validators=[DataRequired()])
    return_notes = TextAreaField('Return Notes (if incomplete or damaged)')
    submit = SubmitField('Process Return')

class DistributionForm(FlaskForm):
    unit_id = SelectField('Unit', coerce=int, validators=[DataRequired()])
    instrument_id = SelectField('Instrument', coerce=int, validators=[DataRequired()])
    notes = TextAreaField('Notes (e.g., quantity)')
    submit = SubmitField('Create Distribution')

    def __init__(self, *args, **kwargs):
        super(DistributionForm, self).__init__(*args, **kwargs)
        self.unit_id.choices = [(u.id, u.name) for u in Unit.query.order_by('name').all()]
        self.instrument_id.choices = [(i.id, i.name) for i in Instrument.query.filter_by(status='in_cssd').order_by('name').all()]

class HandoverForm(FlaskForm):
    receiving_user_id = SelectField('Receiving User', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Confirm Handover')

    def __init__(self, unit_id, *args, **kwargs):
        super(HandoverForm, self).__init__(*args, **kwargs)
        self.receiving_user_id.choices = [(u.id, u.username) for u in User.query.filter_by(unit_id=unit_id).all()]