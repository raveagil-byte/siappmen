from app import create_app, db
from app.models import Unit, Instrument, Transaction
from sqlalchemy import inspect

app = create_app()

with app.app_context():
    print("Dropping all tables...")
    db.drop_all()
    print("Creating all tables...")
    db.create_all()
    print("Tables created.")

    # Verify schema
    inspector = inspect(db.engine)
    columns = [col['name'] for col in inspector.get_columns('transaction')]
    print(f"Transaction table columns: {columns}")


    # Check if units already exist
    if Unit.query.count() == 0:
        units = [
            Unit(name='Emergency Room'),
            Unit(name='Operating Room 1'),
            Unit(name='Operating Room 2'),
            Unit(name='Intensive Care Unit'),
            Unit(name='Pediatrics'),
            Unit(name='Maternity')
        ]
        db.session.bulk_save_objects(units)
        db.session.commit()
        print("Added initial units.")

    # Check if instruments already exist
    if Instrument.query.count() == 0:
        instruments = [
            Instrument(name='Scalpel', description='Standard surgical scalpel', status='available'),
            Instrument(name='Forceps', description='Standard surgical forceps', status='available'),
            Instrument(name='Surgical Scissors', description='Standard surgical scissors', status='available'),
            Instrument(name='Retractor', description='Standard surgical retractor', status='available'),
            Instrument(name='Needle Holder', description='Standard surgical needle holder', status='available'),
            Instrument(name='Suction Tube', description='Standard surgical suction tube', status='available')
        ]
        db.session.bulk_save_objects(instruments)
        db.session.commit()
        print("Added initial instruments.")

    print("Database has been created and seeded.")