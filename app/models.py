from app import db, login_manager
from flask_login import UserMixin
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='unit_user') # 'cssd_user' or 'unit_user'
    unit_id = db.Column(db.Integer, db.ForeignKey('unit.id'))

    def __repr__(self):
        return f"User('{self.username}', '{self.role}')"

class Unit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    users = db.relationship('User', backref='unit', lazy=True)

    def __repr__(self):
        return f"Unit('{self.name}')"

class Instrument(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='available') # 'available', 'in_use', 'in_cssd'

    def __repr__(self):
        return f"Instrument('{self.name}', '{self.status}')"

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    qr_code = db.Column(db.String(100), unique=True, nullable=False)
    instrument_id = db.Column(db.Integer, db.ForeignKey('instrument.id'), nullable=False)
    unit_id = db.Column(db.Integer, db.ForeignKey('unit.id'), nullable=False)
    patient_name = db.Column(db.String(100))
    loan_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    return_date = db.Column(db.DateTime)
    loan_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    return_user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    cssd_loan_officer_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    cssd_return_officer_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    status = db.Column(db.String(20), nullable=False, default='loaned') # loaned, returned, distributed, received
    notes = db.Column(db.Text)
    completeness_status = db.Column(db.String(20), default='complete') # complete, incomplete, damaged
    return_notes = db.Column(db.Text)


    instrument = db.relationship('Instrument', backref='transactions')
    unit = db.relationship('Unit', backref='transactions')
    loan_user = db.relationship('User', foreign_keys=[loan_user_id])
    return_user = db.relationship('User', foreign_keys=[return_user_id])
    cssd_loan_officer = db.relationship('User', foreign_keys=[cssd_loan_officer_id])
    cssd_return_officer = db.relationship('User', foreign_keys=[cssd_return_officer_id])

    def __repr__(self):
        return f"Transaction('{self.qr_code}', '{self.status}')"