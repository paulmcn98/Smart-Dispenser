**Set up guide**
`
# install dependencies
pip3 install -r requirements.txt

# set up mySQL server and create database
python3 create_database.py

# start the server
python3 server.py

# start client in another terminal while server is running(open a new terminal for every client you want to connect the server)
python3 client.py

# preform data analytics on data from mySQL server
python3 data_analytics.py

# run the neural network to the minutes between each use of a dispenser
python3 machine_learning.py`