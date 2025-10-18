from flask import render_template, url_for, flash, redirect, request, Blueprint, jsonify, current_app
from flask_login import login_user, current_user, logout_user, login_required
from app import db, bcrypt
from app.models import User, Unit, Instrument, Transaction
from app.main.forms import RegistrationForm, LoginForm, LoanForm, ReturnForm, DistributionForm, HandoverForm
import qrcode
import uuid
from io import BytesIO
import base64
from datetime import datetime, timedelta


main = Blueprint('main', __name__)

@main.route("/")
@main.route("/home")
def home():
    return render_template('home.html')

@main.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('main.login'))
    return render_template('register.html', title='Register', form=form)


@main.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@main.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('main.home'))

@main.context_processor
def inject_overdue_notifications():
    if current_user.is_authenticated:
        overdue_items = check_overdue_items(current_user)
        return dict(overdue_items=overdue_items)
    return dict(overdue_items=None)

def check_overdue_items(user):
    loan_duration = timedelta(hours=current_app.config['LOAN_DURATION_HOURS'])
    overdue_limit = datetime.utcnow() - loan_duration

    overdue_transactions = Transaction.query.filter(
        Transaction.loan_user_id == user.id,
        Transaction.status == 'loaned',
        Transaction.loan_date < overdue_limit
    ).all()

    return overdue_transactions

@main.route("/loan/new", methods=['GET', 'POST'])
@login_required
def new_loan():
    if check_overdue_items(current_user):
        flash('You have overdue items. Please return them before borrowing new instruments.', 'danger')
        return redirect(url_for('main.home'))

    form = LoanForm()
    if form.validate_on_submit():
        qr_code_data = str(uuid.uuid4())
        transaction = Transaction(qr_code=qr_code_data,
                                  instrument_id=form.instrument_id.data,
                                  unit_id=form.unit_id.data,
                                  patient_name=form.patient_name.data,
                                  loan_user_id=current_user.id,
                                  notes=form.notes.data)
        instrument = Instrument.query.get(form.instrument_id.data)
        instrument.status = 'in_use'
        db.session.add(transaction)
        db.session.commit()
        flash('Loan has been created!', 'success')
        return redirect(url_for('main.view_qr', qr_code=transaction.qr_code))
    return render_template('create_loan.html', title='New Loan', form=form)

@main.route("/qr_code/<qr_code>")
@login_required
def view_qr(qr_code):
    transaction = Transaction.query.filter_by(qr_code=qr_code).first_or_404()

    # Generate QR code image
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(transaction.qr_code)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    # Convert image to base64 string
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()

    return render_template('view_qr.html', title='QR Code', transaction=transaction, img_str=img_str)

@main.route("/return", methods=['GET', 'POST'])
@login_required
def return_instrument():
    form = ReturnForm()
    if form.validate_on_submit():
        transaction = Transaction.query.filter_by(qr_code=form.qr_code.data, status='loaned').first()
        if transaction:
            transaction.return_date = datetime.utcnow()
            transaction.return_user_id = current_user.id
            transaction.status = 'returned'
            transaction.completeness_status = form.completeness_status.data
            transaction.return_notes = form.return_notes.data
            instrument = Instrument.query.get(transaction.instrument_id)
            instrument.status = 'in_cssd'
            db.session.commit()
            flash('Instrument has been returned!', 'success')
            return redirect(url_for('main.home'))
        else:
            flash('Invalid or already returned QR Code.', 'danger')
    return render_template('return_instrument.html', title='Return Instrument', form=form)


@main.route('/scan')
@login_required
def scan():
    return render_template('scan.html', title='Scan QR Code')

@main.route('/get_transaction_by_qr/<qr_code>')
@login_required
def get_transaction_by_qr(qr_code):
    transaction = Transaction.query.filter_by(qr_code=qr_code).first()
    if transaction:
        return jsonify({
            'id': transaction.id,
            'instrument': transaction.instrument.name,
            'unit': transaction.unit.name,
            'loan_date': transaction.loan_date.strftime('%Y-%m-%d %H:%M:%S'),
            'status': transaction.status
        })
    return jsonify({'error': 'Transaction not found'}), 404

@main.route("/dashboard")
@login_required
def dashboard():
    # Report:
    # - nama unit
    # - jumlah instrumen kotor setiap hari (today's returns)
    # - pengiriman instrumen steril (today's loans/distributions)
    # - jumlah instrumen yang belum balik ke CSSD (outstanding loans)
    # - serta jumlah alat yang tidak komplit. (incomplete/damaged returns)

    today = datetime.utcnow().date()
    start_of_day = datetime.combine(today, datetime.min.time())
    end_of_day = datetime.combine(today, datetime.max.time())

    units = Unit.query.order_by(Unit.name).all()
    report_data = []

    for unit in units:
        daily_returns = Transaction.query.filter(
            Transaction.unit_id == unit.id,
            Transaction.return_date >= start_of_day,
            Transaction.return_date <= end_of_day
        ).count()

        daily_loans = Transaction.query.filter(
            Transaction.unit_id == unit.id,
            Transaction.loan_date >= start_of_day,
            Transaction.loan_date <= end_of_day
        ).count()

        outstanding_loans = Transaction.query.filter(
            Transaction.unit_id == unit.id,
            Transaction.status.in_(['loaned', 'distributed'])
        ).count()

        incomplete_returns = Transaction.query.filter(
            Transaction.unit_id == unit.id,
            Transaction.completeness_status.in_(['incomplete', 'damaged'])
        ).count()

        report_data.append({
            'unit_name': unit.name,
            'daily_returns': daily_returns,
            'daily_loans': daily_loans,
            'outstanding_loans': outstanding_loans,
            'incomplete_returns': incomplete_returns
        })

    return render_template('dashboard.html', title='Dashboard', report_data=report_data)

@main.route("/distribute/new", methods=['GET', 'POST'])
@login_required
def new_distribution():
    form = DistributionForm()
    if form.validate_on_submit():
        qr_code_data = str(uuid.uuid4())
        transaction = Transaction(qr_code=qr_code_data,
                                  instrument_id=form.instrument_id.data,
                                  unit_id=form.unit_id.data,
                                  cssd_loan_officer_id=current_user.id,
                                  status='distributed',
                                  notes=form.notes.data)
        instrument = Instrument.query.get(form.instrument_id.data)
        instrument.status = 'in_use'
        db.session.add(transaction)
        db.session.commit()
        flash('Distribution has been created!', 'success')
        return redirect(url_for('main.view_qr', qr_code=transaction.qr_code))
    return render_template('create_distribution.html', title='New Distribution', form=form)

@main.route("/handover/<int:transaction_id>", methods=['GET', 'POST'])
@login_required
def handover(transaction_id):
    transaction = Transaction.query.get_or_404(transaction_id)
    if transaction.status != 'distributed':
        flash('This transaction is not awaiting handover.', 'warning')
        return redirect(url_for('main.home'))

    form = HandoverForm(unit_id=transaction.unit_id)
    if form.validate_on_submit():
        transaction.cssd_return_officer_id = current_user.id
        transaction.return_user_id = form.receiving_user_id.data
        transaction.return_date = datetime.utcnow()
        transaction.status = 'received'
        db.session.commit()
        flash('Handover complete!', 'success')
        return redirect(url_for('main.home'))
    return render_template('handover.html', title='Handover', form=form, transaction=transaction)