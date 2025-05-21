import click
import uuid
from datetime import datetime
from flask.cli import with_appcontext
from app import db
from app.models import User

def register_cli_commands(app):
    @app.cli.command('init-db')
    @with_appcontext
    def init_db():
        """Initialize the database."""
        db.create_all()
        click.echo('Initialized the database.')
    
    @app.cli.command('drop-db')
    @with_appcontext
    def drop_db():
        """Drop the database."""
        if click.confirm('Are you sure you want to drop all tables?'):
            db.drop_all()
            click.echo('Dropped all tables.')
    
    @app.cli.command('create-admin')
    @click.argument('email')
    @click.argument('name')
    @click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True)
    @with_appcontext
    def create_admin(email, name, password):
        """Create an admin user."""
        try:
            admin = User.query.filter_by(email=email).first()
            if admin:
                click.echo(f'Admin with email {email} already exists.')
                return
            
            admin = User(
                id=str(uuid.uuid4()),
                email=email,
                name=name,
                role='admin',
                is_active=True,
                last_login=None,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            admin.set_password(password)
            
            db.session.add(admin)
            db.session.commit()
            click.echo(f'Admin user {email} created successfully.')
        except Exception as e:
            db.session.rollback()
            click.echo(f'Error creating admin user: {str(e)}')
    
    @app.cli.command('seed-db')
    @with_appcontext
    def seed_db():
        """Seed the database with sample data."""
        from app.utils.seed_data import seed_database
        if click.confirm('Are you sure you want to seed the database? This will add sample data.'):
            try:
                seed_database()
                click.echo('Database seeded successfully.')
            except Exception as e:
                click.echo(f'Error seeding database: {str(e)}')
    
    @app.cli.command('list-users')
    @with_appcontext
    def list_users():
        """List all users in the database."""
        try:
            users = User.query.all()
            if not users:
                click.echo('No users found.')
                return
            
            click.echo(f"{'ID':<37} {'Email':<30} {'Name':<20} {'Role':<10}")
            click.echo('-' * 100)
            for user in users:
                click.echo(f"{user.id:<37} {user.email:<30} {user.name:<20} {user.role:<10}")
            click.echo(f"\nTotal users: {len(users)}")
        except Exception as e:
            click.echo(f'Error listing users: {str(e)}') 