import argparse
from app import create_app, db, bcrypt
from app.models import User, Unit, Instrument, Transaction
from sqlalchemy import inspect

def create_database(create_users=False):
    """Creates and seeds the database."""
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

        # Seed Units
        if Unit.query.count() == 0:
            units = [
                Unit(name='Emergency Room'), # id=1
                Unit(name='Operating Room'), # id=2
                Unit(name='Intensive Care Unit'), # id=3
                Unit(name='Pediatrics'), # id=4
            ]
            db.session.bulk_save_objects(units)
            db.session.commit()
            print("Added initial units.")

        # Seed Instruments
        if Instrument.query.count() == 0:
            instruments = [
                Instrument(name='Scalpel', status='available'), # id=1
                Instrument(name='Forceps', status='available'), # id=2
                Instrument(name='Surgical Scissors', status='available'), # id=3
            ]
            db.session.bulk_save_objects(instruments)
            db.session.commit()
            print("Added initial instruments.")

        # Seed Users if requested
        if create_users:
            if User.query.count() == 0:
                hashed_password = bcrypt.generate_password_hash('password').decode('utf-8')
                users = [
                    User(username='cssd_user', password=hashed_password, role='cssd_user', unit_id=None),
                    User(username='er_user', password=hashed_password, role='unit_user', unit_id=1), # Emergency Room
                    User(username='or_user', password=hashed_password, role='unit_user', unit_id=2), # Operating Room
                ]
                db.session.bulk_save_objects(users)
                db.session.commit()
                print("Added test users (cssd_user, er_user, or_user) with password 'password'.")

        print("Database has been created and seeded.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Manage the database.')
    parser.add_argument('--create-users', action='store_true', help='Create test users along with the database.')
    args = parser.parse_args()

    create_database(create_users=args.create_users)