from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy 
from flask_marshmallow import Marshmallow 
import os
from flask_socketio import SocketIO, send, emit
 
#List of dispensers connected to the server
list_of_dispensers = []

#Initialise app
app = Flask(__name__)

#Dispensers Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:intragroup16@localhost/dispenserdb' 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#Initialise db
db = SQLAlchemy(app)
#Initialise ma
ma = Marshmallow(app)
#Initialise socketio
socketio = SocketIO(app)

#When a new client connects to the server
@socketio.on('connect')
def connect():
    global list_of_dispensers
    #client session id
    new_client_id = request.sid
    list_of_dispensers.append(new_client_id)
    print('Device ' + request.sid + " is connected")
    
                                
#Dispenser class
class Dispenser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.String(100))
    date = db.Column(db.String(100))
    time = db.Column(db.Integer)
    fluid_dispensed = db.Column(db.Float)
    fluid_level = db.Column(db.Float)
    used = db.Column(db.Integer)
    ignored = db.Column(db.Integer)
  
    def __init__(self, device_id, date, time, fluid_dispensed, fluid_level, used, ignored):
      self.device_id = device_id
      self.date = date
      self.time = time
      self.fluid_dispensed = fluid_dispensed
      self.fluid_level = fluid_level
      self.used = used
      self.ignored = ignored

#Dispenser Schema
class Dispenser_schema(ma.Schema):
    class Meta:
      fields = ('id', 'device_id', 'date', 'time', 'fluid_dispensed', 'fluid_level', 'used', 'ignored')

#Initialise schema
dispenser_schema = Dispenser_schema()
dispensers_schema = Dispenser_schema(many=True)

#Add a new dispenser data input to the database
@app.route('/dispenserdb', methods=['POST'])
def add_dispenser():
    device_id = request.json['device_id']
    date = request.json['date']
    time = request.json['time']
    fluid_dispensed = request.json['fluid_dispensed']
    fluid_level = request.json['fluid_level']
    used = request.json['used']
    ignored = request.json['ignored']
  
    new_dispenser = Dispenser(device_id, date, time, fluid_dispensed, fluid_level, used, ignored)
  
    db.session.add(new_dispenser)
    db.session.commit()
  
    return dispenser_schema.jsonify(new_dispenser)

#Update an existing dispenser in the database
@app.route('/dispenserdb/<id>', methods=['PUT'])
def update_dispenser(id):
    dispenser = Dispenser.query.get(id)
  
    device_id = request.json['device_id']
    date = request.json['date']
    time = request.json['time']
    fluid_dispensed = request.json['fluid_dispensed']
    fluid_level = request.json['fluid_level']
    used = request.json['used']
    ignored = request.json['ignored']
  
    dispenser.device_id = device_id
    dispenser.date = date
    dispenser.time = time
    dispenser.fluid_dispensed = fluid_dispensed
    dispenser.fluid_level = fluid_level
    dispenser.used += used
    dispenser.ignored += ignored
  
    db.session.commit()
  
    return dispenser_schema.jsonify(dispenser)

# Get all data entrys in table for a dispenser
@app.route('/dispenserdb', methods=['GET'])
def get_data():
  all_data = Dispenser.query.all()
  result = dispensers_schema.dump(all_data)
  return jsonify(result)


# Run the server
if __name__ == '__main__':
  socketio.run(app)