from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy 
from flask_marshmallow import Marshmallow 
import os


#Initialise app
app = Flask(__name__)

#Dispensers Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:intragroup16@localhost/dispenserdb' 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#Initialise db
db = SQLAlchemy(app)
# Init ma
ma = Marshmallow(app)

#Dispenser class
class Dispenser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(100))
    time = db.Column(db.String(10))
    fluid_dispensed = db.Column(db.Float)
    fluid_level = db.Column(db.Float)
    times_used = db.Column(db.Integer)
    times_ignored = db.Column(db.Integer)
  
    def __init__(self, date, time, fluid_dispensed, fluid_level, times_used, times_ignored):
      self.date = date
      self.time = time
      self.fluid_dispensed = fluid_dispensed
      self.fluid_level = fluid_level
      self.times_used = times_used
      self.times_ignored = times_ignored

#Dispenser Schema
class Dispenser_schema(ma.Schema):
    class Meta:
      fields = ('id', 'date', 'time', 'fluid_dispensed', 'fluid_level', 'times_used', 'times_ignored')

#Initialise schema
dispenser_schema = Dispenser_schema()
dispensers_schema = Dispenser_schema(many=True)

#Add a new dispenser device to the database
@app.route('/dispenserdb', methods=['POST'])
def add_dispenser():
    date = request.json['date']
    time = request.json['time']
    fluid_dispensed = request.json['fluid_dispensed']
    fluid_level = request.json['fluid_level']
    times_used = request.json['times_used']
    times_ignored = request.json['times_ignored']
  
    new_dispenser = Dispenser(date, time, fluid_dispensed, fluid_level, times_used, times_ignored)
  
    db.session.add(new_dispenser)
    db.session.commit()
  
    return dispenser_schema.jsonify(new_dispenser)

#Update an existing dispenser in the database
@app.route('/dispenserdb/<id>', methods=['PUT'])
def update_dispenser(id):
    dispenser = Dispenser.query.get(id)
  
    date = request.json['date']
    time = request.json['time']
    fluid_dispensed = request.json['fluid_dispensed']
    fluid_level = request.json['fluid_level']
    times_used = request.json['times_used']
    times_ignored = request.json['times_ignored']
  
    dispenser.date = date
    dispenser.time = time
    dispenser.fluid_dispensed = fluid_dispensed
    dispenser.fluid_level = fluid_level
    dispenser.times_used += times_used
    dispenser.times_ignored += times_ignored
  
    db.session.commit()
  
    return dispenser_schema.jsonify(dispenser)

#Delete a dispenser data from the table
@app.route('/dispenserdb/<id>', methods=['DELETE'])
def delete_product(id):
    dispenser = Dispenser.query.get(id)
    db.session.delete(dispenser)
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
  app.run(debug=True)