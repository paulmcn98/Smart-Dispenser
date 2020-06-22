import sys
import requests
import json
import time
import random
import datetime
import server
import socketio

class Device():
    def __init__(self, sid):
        #session id will be used as device id
        self.id = sid
        ip_address = "127.0.0.1"
        port = 5000
        self.url = "http://{}:{}/dispenserdb".format(ip_address, port)
        #starting fluid level when dispenser is full
        self.fluid_level = 1000.00
        Device.create_table()   
        

    #Create table if one does not already exist
    def create_table():
        from server import db
        db.create_all()
        print("Table created")

    #Function for picking random date when generating data
    def random_date():
        start_date = datetime.date(2020, 5, 1)
        end_date = datetime.date(2020, 5, 30)
        
        time_between_dates = end_date - start_date
        days_between_dates = time_between_dates.days
        random_number_of_days = random.randrange(days_between_dates)
        random_date = start_date + datetime.timedelta(days=random_number_of_days)
        date = str(random_date)
        return date

    def random_time():
        hours = ['09', '10', '11', '12','13', '14', '15', '16', '17', '18']
        minutes = ['00', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31', '32', '33', '34', '35', '36', '37', '38', '39', '40', '41', '42', '43', '44', '45', '46', '47', '48', '49', '50', '51', '52', '53', '54', '55', '56', '57', '58', '59']
        hour = random.choice(hours)
        minute = random.choice(minutes)

        return (hour + ':' + minute)


    def send_data(self):
        #Whether dispenser was used or not when motion was detected
        used_or_ignored = random.choice([1,0])
        if used_or_ignored == 0:
            sensor_reading = 0
            used = 0
            ignored = 1
        else:
            used = 1
            ignored = 0
            #all data is random for purposes of example
            sensor_reading = round(random.uniform(5,8), 2)
            self.fluid_level -= sensor_reading
        #generate a random time between 9am and 7pm in 24h format
        time = Device.random_time()
        #generate a random date
        date = Device.random_date()
        #random data
        data = { "device_id": self.id,
                  "date": date,
                  "time": time,    
                  "fluid_dispensed": sensor_reading,    
                  "fluid_level": self.fluid_level,    
                  "used": used,
                  "ignored": ignored}

        #If the fluid level drops below 100mls then it should be refilled asap
        if self.fluid_level <= 100.00:
            self.fluid_level = 1000.00
        #sending data to server
        response = requests.request("POST", self.url, json=data)
        #determine if server recieved data or not
        if response.status_code == 200:
            return ("The server has recieved new data and added to database")
        else:
            return ("Server failed to recieve data")

def main():
    #connect to server
    sio = socketio.Client()
    sio.connect('http://127.0.0.1:5000')
    #Get the session id
    print('Device id is', sio.sid)
    client = Device(sio.sid)
    #infinite client loop
    while True:
        #substitute input from keyboard for the motion sensor connected to raspberry pi board
        keyboard_input = sys.stdin.readline()
        sys.stdout.write("motion detected\n")
        #wait 5 seconds after motion is detected for user to use dispenser if they choose too
        time.sleep(5)
        print(client.send_data())

if __name__ == '__main__':
    main()