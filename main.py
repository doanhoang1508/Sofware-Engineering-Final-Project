from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, current_user, logout_user, login_required
import os
from subprocess import Popen
basedir = os.path.abspath(os.path.dirname(__file__))

# Initialize the app and set up the database
app = Flask(__name__)
app.config['SECRET_KEY'] = '123456'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'instance', 'smart_home.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Initialize the LoginManager
login_manager = LoginManager()
login_manager.init_app(app)

# Define the User, Room, and Device models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))
    first_name = db.Column(db.String(30))
    floors = db.relationship('Floor', backref='user')
    rooms =  db.relationship('Room', backref='user')
    devices =  db.relationship('Device', backref='user')

class Floor(db.Model):
    floor_id = db.Column(db.Integer, primary_key=True)
    floor_number= db.Column(db.String(50))
    floor_relationship = db.relationship('Room', backref ='floor')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
   

class Room(db.Model):
    room_id = db.Column(db.Integer, primary_key=True)
    type_of_room = db.Column(db.String(80))
    devices = db.Column(db.String())
    number_of_floor_id = db.Column(db.Integer, db.ForeignKey('floor.floor_id'), nullable = False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    device_relationship = db.relationship('Device', backref='room')
        
class Device(db.Model):
    device_id = db.Column(db.Integer, primary_key=True)
    device_name = db.Column(db.String(80), nullable=False)
    device_tatus = db.Column(db.Boolean(), default = False)
    room_id = db.Column(db.Integer, db.ForeignKey('room.room_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

@app.route('/devices')
def devices():
    devices = Device.query.all()
    print(devices) # this will print the devices variable to the terminal
    return render_template('devices.html', devices=devices)

    
# Define the login_required and current_user functions
@login_manager.user_loader
def load_user(user_id):
    # Your code to load the user from the database
    return User.query.get(int(user_id))

@login_manager.unauthorized_handler
def unauthorized():
    return redirect(url_for('login'))

@app.route('/')
def index():
    return render_template('home_before_login.html')

# Define the routes for registering, logging in
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # get the data from the form
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        if len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            new_user = User(email=email,first_name=first_name, password=generate_password_hash(password1, method='sha256'))
            db.session.add(new_user)
            db.session.flush()
            db.session.commit()

            for floor_number in range(1, 4):
                floor = Floor(floor_number=f'Floor {floor_number}', user_id=new_user.id)
                db.session.add(floor)
                db.session.flush()
            db.session.commit()
            
            login_user(new_user, remember=True)
            flash('Account created!', category='success')
            return redirect(url_for('login'))
    return render_template("register.html", user=current_user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                login_user(user, remember=True)
                return redirect(url_for('hello_user'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')
    return render_template("login.html", user=current_user)

@app.route('/home', methods=['POST', 'GET'])
def hello_user():
    return render_template('home_after_login.html', data = current_user.first_name)

@app.route('/floor-1-rooms-devices')
@login_required
def floor_1_rooms_devices():
    # Query all rooms and devices of the current user where the floor_number is "Floor 1"
    rooms = Room.query.join(Floor).filter(Room.user_id == current_user.id, Floor.floor_number == 'Floor 1').all()

    # Render a template to display the data
    return render_template('floor_1.html', rooms=rooms)

@app.route('/floor-2-rooms-devices')
@login_required
def floor_2_rooms_devices():
    # Query all rooms and devices of the current user where the floor_number is "Floor 1"
    rooms = Room.query.join(Floor).filter(Room.user_id == current_user.id, Floor.floor_number == 'Floor 2').all()

    # Render a template to display the data
    return render_template('floor_2.html', rooms=rooms)

@app.route('/floor-3-rooms-devices')
@login_required
def floor_3_rooms_devices():
    # Query all rooms and devices of the current user where the floor_number is "Floor 1"
    rooms = Room.query.join(Floor).filter(Room.user_id == current_user.id, Floor.floor_number == 'Floor 3').all()
    # Render a template to display the data
    return render_template('floor_3.html', rooms=rooms)

@app.route('/floor-1-rooms-devices/<int:room_id>', methods=['GET'])
@login_required
def view_devices_1(room_id):
    room = Room.query.filter_by(room_id=room_id, user_id=current_user.id).first_or_404()
    devices = Device.query.filter_by(room_id=room_id).all()
    return render_template('dv_floor_1.html', devices=devices, room =room, data1=room.type_of_room)

@app.route('/floor-2-rooms-devices/<int:room_id>', methods=['GET'])
@login_required
def view_devices_2(room_id):
    room = Room.query.filter_by(room_id=room_id, user_id=current_user.id).first_or_404()
    devices = Device.query.filter_by(room_id=room_id).all()
    return render_template('dv_floor_2.html', devices=devices, room =room, data2=room.type_of_room)

@app.route('/floor-3-rooms-devices/<int:room_id>', methods=['GET'])
@login_required
def view_devices_3(room_id):
    room = Room.query.filter_by(room_id=room_id, user_id=current_user.id).first_or_404()
    devices = Device.query.filter_by(room_id=room_id).all()
    return render_template('dv_floor_3.html', devices=devices, room =room, data3=room.type_of_room)

@app.route('/createpage1' , methods = ['GET','POST'])
@login_required
def createpage1():
    if request.method == 'GET':
        return render_template('createpage.html')

    if request.method == 'POST':
        floor= Floor.query.filter_by(floor_number = 'Floor 1', user_id=current_user.id).first()
        if floor:
            device = request.form.getlist('devices')
            #devices = ','.join(map(str, devices))
            devices=" | ".join(map(str, device))
            print(devices)
            #devices = devices
            type_of_room = request.form.get('type_of_room')
            floor_id = floor.floor_id
            rooms = Room(
                devices=devices,
                type_of_room = type_of_room,
                user_id = current_user.id,
                number_of_floor_id = floor_id
            )
        db.session.add(rooms)
        db.session.commit()

        devices_list = devices.split(" | ")
        for device in devices_list:
            device = Device(device_name=device, user_id = current_user.id,room_id=rooms.room_id)
            db.session.add(device)
        db.session.commit()
        return redirect(url_for('floor_1_rooms_devices'))
    return render_template('floor_1.html')

@app.route('/createpage2' , methods = ['GET','POST'])
@login_required
def createpage2():
    if request.method == 'GET':
        return render_template('createpage.html')

    if request.method == 'POST':
        floor= Floor.query.filter_by(floor_number = 'Floor 2', user_id=current_user.id).first()
        if floor:
            device = request.form.getlist('devices')
            #devices = ','.join(map(str, devices))
            devices=" | ".join(map(str, device))
            #devices = devices
            type_of_room = request.form.get('type_of_room')
            floor_id = floor.floor_id
            rooms = Room(
                devices=devices,
                type_of_room = type_of_room,
                user_id = current_user.id,
                number_of_floor_id = floor_id
            )
        db.session.add(rooms)
        db.session.commit()

        devices_list = devices.split(" | ")
        for device in devices_list:
            device = Device(device_name=device, user_id = current_user.id,room_id=rooms.room_id)
            db.session.add(device)
        db.session.commit()
        return redirect(url_for('floor_2_rooms_devices'))
    return render_template('floor_2.html')

@app.route('/createpage3' , methods = ['GET','POST'])
@login_required
def createpage3():
    if request.method == 'GET':
        return render_template('createpage.html')
    if request.method == 'POST':
        floor= Floor.query.filter_by(floor_number = 'Floor 3', user_id=current_user.id).first()
        if floor:
            device = request.form.getlist('devices')
            #devices = ','.join(map(str, devices))
            devices=" | ".join(map(str, device))
            #devices = devices
            type_of_room = request.form.get('type_of_room')
            floor_id = floor.floor_id
            rooms = Room(
                devices=devices,
                type_of_room = type_of_room,
                user_id = current_user.id,
                number_of_floor_id = floor_id
            )
        db.session.add(rooms)
        db.session.commit()

        devices_list = devices.split(" | ")
        for device in devices_list:
            device = Device(device_name=device, user_id = current_user.id,room_id=rooms.room_id)
            db.session.add(device)
        db.session.commit()
        return redirect(url_for('floor_3_rooms_devices'))
    return render_template('floor_3.html')

@app.route('/floor-1-rooms-devices/<int:room_id>/delete', methods=['GET','POST'])
@login_required
def delete_1(room_id):
    # Query the room to be deleted
    room = Room.query.filter_by(room_id=room_id, user_id=current_user.id).first()

    # If the room exists, delete it and its associated devices
    if room:
        # Delete the devices associated with the room
        Device.query.filter_by(room_id=room_id, user_id=current_user.id).delete()

        # Delete the room
        db.session.delete(room)
        db.session.commit()

        flash('Room and associated devices deleted successfully!', category='success')
    else:
        flash('Room not found!', category='error')

    # Redirect back to the floor 1 page
    return redirect(url_for('floor_1_rooms_devices'))

@app.route('/floor-2-rooms-devices/<int:room_id>/delete', methods=['GET','POST'])
@login_required
def delete_2(room_id):
    # Query the room to be deleted
    room = Room.query.filter_by(room_id=room_id, user_id=current_user.id).first()

    # If the room exists, delete it and its associated devices
    if room:
        # Delete the devices associated with the room
        Device.query.filter_by(room_id=room_id, user_id=current_user.id).delete()

        # Delete the room
        db.session.delete(room)
        db.session.commit()

        flash('Room and associated devices deleted successfully!', category='success')
    else:
        flash('Room not found!', category='error')

    # Redirect back to the floor 2 page
    return redirect(url_for('floor_2_rooms_devices'))

@app.route('/floor-3-rooms-devices/<int:room_id>/delete', methods=['GET','POST'])
@login_required
def delete_3(room_id):
    # Query the room to be deleted
    room = Room.query.filter_by(room_id=room_id, user_id=current_user.id).first()

    # If the room exists, delete it and its associated devices
    if room:
        # Delete the devices associated with the room
        Device.query.filter_by(room_id=room_id, user_id=current_user.id).delete()

        # Delete the room
        db.session.delete(room)
        db.session.commit()

        flash('Room and associated devices deleted successfully!', category='success')
    else:
        flash('Room not found!', category='error')

    # Redirect back to the floor 3 page
    return redirect(url_for('floor_3_rooms_devices'))

@app.route('/help_info')
@login_required
def helf_info():
    return render_template('help_info.html')

# handle the logout route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/start')
@login_required
def start():
    Popen(['python', 'D://học onl/SE project/Software Engineering/Software Engineering/hand-gestures-smart-home-main/main.py'])
    return 'Success'
'''
# Define the route for viewing the status of a room
@app.route('/room_status/<room_id>')
@login_required
def room_status(room_id):
    # Retrieve the room using the room_id
    room = Room.query.get_or_404(room_id)

    # Retrieve all the devices associated with the room
    devices = Device.query.filter_by(room_id=room.id)

    # Initialize a dictionary to store the status of each type of device
    room_status = {}

    # Loop through each device and update the room_status dictionary
    for device in devices:
        if device.device_type == "temperature_sensor":
            room_status["temperature"] = device.status
        elif device.device_type == "moisture_sensor":
            room_status["moisture"] = device.status
        elif device.device_type == "light_sensor":
            room_status["light_condition"] = device.status
        elif device.device_type == "air_conditioner":
            room_status["air_condition"] = device.status
        # Add more elif blocks for other device types as needed

    # Render the room_status template and pass in the room and room_status data
    return render_template('room_status.html', room=room, room_status=room_status)
'''
# Run the app
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)


