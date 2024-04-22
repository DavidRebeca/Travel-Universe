from flask import Blueprint, request, jsonify, session
from models import db, Destination, Users, Reservation, format_users,format_destination,format_reservation
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity

# Create a Blueprint for routes
routes_bp = Blueprint('routes', __name__)

# Create a destination
@routes_bp.route('/destination', methods=['POST'])
@jwt_required()
def create_destination():
    title = request.json['title']
    location = request.json['location']
    description = request.json.get('description', '')  # optional field
    price = request.json['price']
    discount = request.json['discount']
    destination = Destination(title, location, description, price, discount)
    db.session.add(destination)
    db.session.commit()
    return format_destination(destination)

# Get all destinations
@routes_bp.route('/destination', methods=['GET'])
@jwt_required()
def get_destinations():
    destinations = Destination.query.order_by(Destination.id.asc()).all()
    destinations_list = []
    for destination in destinations:
        destinations_list.append(format_destination(destination))
    return {'destinations': destinations_list}

@routes_bp.route('/available_destinations', methods=['GET'])
@jwt_required()
def get_available_destinations():
    check_in_date = request.args.get('check_in_date')
    check_out_date = request.args.get('check_out_date')

    if not (check_in_date and check_out_date):
        return jsonify({'message': 'Please provide check_in_date and check_out_date parameters'}), 400

    try:
        check_in_date = datetime.strptime(check_in_date, '%Y-%m-%d')
        check_out_date = datetime.strptime(check_out_date, '%Y-%m-%d')
    except ValueError:
        return jsonify({'message': 'Invalid date format. Please provide dates in YYYY-MM-DD format'}), 400

    # Query reservations that overlap with the specified interval
    overlapping_reservations = Reservation.query.filter(
        (Reservation.check_in_date <= check_out_date) &
        (Reservation.check_out_date >= check_in_date)
    ).all()

    overlapping_destination_ids = {reservation.destination_id for reservation in overlapping_reservations}

    # Query destinations that are not in the overlapping reservations
    available_destinations = Destination.query.filter(
        ~Destination.id.in_(overlapping_destination_ids)
    ).all()

    if not available_destinations:
        return jsonify({'message': 'No available destinations for the specified interval'}), 404

    available_destinations_list = []
    for destination in available_destinations:
        available_destinations_list.append(format_destination(destination))

    return {'available_destinations': available_destinations_list}

# Get destination by id
@routes_bp.route('/destination/<id>', methods=['GET'])
@jwt_required()
def get_destination(id):
    destination = Destination.query.filter_by(id=id).first()
    formatted_destination = format_destination(destination)
    return {'destination': formatted_destination}

# Delete a destination
@routes_bp.route('/destination/<id>', methods=['DELETE'])
@jwt_required()
def delete_destination(id):
    destination = Destination.query.filter_by(id=id).first()
    db.session.delete(destination)
    db.session.commit()
    return f'Deleted destination: {id}'

# Update a destination
@routes_bp.route('/destination/<id>', methods=['PUT'])
@jwt_required()
def update_destination(id):
    destination = Destination.query.filter_by(id=id).first()
    title = request.json['title']
    description = request.json.get('description', destination.description)  # optional field
    price = request.json['price']
    discount = request.json['discount']
    destination.title = title
    destination.description = description
    destination.price = price
    destination.discount = discount
    db.session.commit()
    return {'destination': format_destination(destination)}

@routes_bp.route('/user/<username>', methods=['GET'])
def get_user_by_username(username):
    user = Users.query.filter_by(username=username).first()
    if user:
        formatted_user = format_users(user)
        return {'user': formatted_user}
    else:
        return jsonify({'message': 'User not found'}), 404

# Create a reservation
@routes_bp.route('/reservation', methods=['POST'])
@jwt_required()
def create_reservation():
    user_id = request.json['user_id']
    destination_id = request.json['destination_id']
    check_in_date = request.json['check_in_date']
    check_out_date = request.json['check_out_date']
    total_price = request.json['total_price']
    reservation = Reservation(user_id, destination_id, check_in_date, check_out_date, total_price)
    db.session.add(reservation)
    db.session.commit()
    return format_reservation(reservation)

# Get all reservations
@routes_bp.route('/reservation/<id>', methods=['GET'])
@jwt_required()
def get_reservations(id):
    reservations = Reservation.query.filter_by(destination_id=id).all()
    if not reservations:
        return jsonify({'message': 'No reservations found for the specified destination_id'}), 404
    reservations_list = []
    for reservation in reservations:
        reservations_list.append(format_reservation(reservation))
    return {'reservations': reservations_list}

# Register User
@routes_bp.route('/register', methods=['POST'])
def register():
    name = request.json['name']
    username = request.json['username']
    password = request.json['password']
    role = request.json['role']

    hashed_password = generate_password_hash(password)
    user = Users(name, username, hashed_password, role)

    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'User registered successfully'})

# Login
# Create access token for authentication
@routes_bp.route('/login', methods=['POST'])
def login():
    username = request.json['username']
    password = request.json['password']

    user = Users.query.filter_by(username=username).first()
    if user and check_password_hash(user.password, password):
        access_token = create_access_token(identity=username)
        return jsonify({'access_token': access_token}), 200
    else:
        return jsonify({'message': 'Invalid username or password'}), 401

# Logout
@routes_bp.route('/logout')
def logout():
    session.clear()
    return jsonify({'message': 'Logged out successfully'})

@routes_bp.route('/unavailable_dates/<destination_id>', methods=['GET'])
def get_unavailable_dates(destination_id):
    try:
        # Parse destination_id to an integer
        destination_id = int(destination_id)
    except ValueError:
        return jsonify({'message': 'Invalid destination ID'}), 400

    # Query reservations for the specified destination
    reservations = Reservation.query.filter_by(destination_id=destination_id).all()

    # Initialize a list to store unavailable dates
    unavailable_dates = []

    # Loop through each reservation
    for reservation in reservations:
        # Extract check-in and check-out dates
        check_in_date = reservation.check_in_date
        check_out_date = reservation.check_out_date

        # Generate a list of dates between check-in and check-out dates
        current_date = check_in_date
        while current_date <= check_out_date:
            # Append the date to the list of unavailable dates
            unavailable_dates.append(current_date.strftime('%Y-%m-%d'))
            # Move to the next date
            current_date += timedelta(days=1)
    return jsonify({'unavailable_dates': unavailable_dates})
