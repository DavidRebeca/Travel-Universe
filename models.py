from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Destination(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(100))
    price = db.Column(db.Float, nullable=False)
    discount = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"Destination: {self.title}, Location: {self.location}"

    def __init__(self, title, location, description, price, discount):
        self.title = title
        self.location = location
        self.description = description
        self.price = price
        self.discount = discount

def format_destination(destination):
  return{
            "id": destination.id,
            "title": destination.title,
            "location": destination.location,
            "description": destination.description,
            "price": destination.price,
            "discount": destination.discount
        }

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    role = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return f"User: {self.name}, Username: {self.username}, Role: {self.role}"

    def __init__(self, name, username, password, role):
        self.name = name
        self.username = username
        self.password = password
        self.role = role

def format_users(user):
  return{
            "id": user.id,
            "name": user.name,
            "username": user.username,
            "password": user.password,
            "role": user.role
        }
class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    destination_id = db.Column(db.Integer, db.ForeignKey('destination.id'), nullable=False)
    check_in_date = db.Column(db.DateTime, nullable=False)
    check_out_date = db.Column(db.DateTime, nullable=False)
    total_price = db.Column(db.Float, nullable=False)

    # Define relationships
    user = db.relationship('Users', foreign_keys=[user_id], backref='reservations')
    destination = db.relationship('Destination', foreign_keys=[destination_id], backref='reservations')

    def __repr__(self):
        return f"Reservation: ID-{self.id}, User: {self.user_id}, Destination: {self.destination_id}, Check-in: {self.check_in_date}, Check-out: {self.check_out_date}, Total Price: {self.total_price}"

    def __init__(self, user_id, destination_id, check_in_date, check_out_date, total_price):
        self.user_id = user_id
        self.destination_id = destination_id
        self.check_in_date = check_in_date
        self.check_out_date = check_out_date
        self.total_price = total_price

def format_reservation(reservation):
  return{
            "id": reservation.id,
            "user_id": reservation.user_id,
            "destination_id": reservation.destination_id,
            "check_in_date": reservation.check_in_date,
            "check_out_date": reservation.check_out_date,
            "total_price": reservation.total_price
        }