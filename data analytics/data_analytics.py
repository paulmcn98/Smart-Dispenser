import mysql.connector

#connect to mysql
mydb = mysql.connector.connect(
	host="localhost",
	user="root",
	passwd="intragroup16",
	database="dispenserdb"
)
mycursor = mydb.cursor()

#mySQL query
mycursor.execute("SELECT device_id FROM dispenserdb.dispenser")
result = mycursor.fetchall()

#Total times motion was detected by all dispensers
motion_detected = len(result)
device_ids = [] 
for row in result:
	if row[0] not in device_ids:
		device_ids.append(row[0])

#mySQL query
mycursor.execute("SELECT device_id, used, ignored FROM dispenserdb.dispenser")
result = mycursor.fetchall()

#Data analytocs for all devices in the database
times_used = 0
times_ignored = 0
for row in result:
	if row[1] == 1:
		times_used += 1
	elif row[2] == 1:
		times_ignored += 1
print('Data for all devices from database:\nTimes motion was detected: {}\nTimes dispenser was used: {}, {:.2f}%\nTimes dispenser was ignored: {}, {:.2f}%\n'.format(str(times_used+times_ignored), str(times_used), times_used/(times_used+times_ignored)*100, str(times_ignored), times_ignored/(times_used+times_ignored)*100))

#data for each individual device in the database
for s in device_ids:
	times_used = 0
	times_ignored = 0
	for row in result:
		if row[0] == s:
		    if row[1] == 1:
		    	times_used += 1
		    elif row[2] == 1:
		    	times_ignored += 1
	print('Device: {}\nTimes motion was detected: {}\nTimes dispenser was used: {}, {:.2f}%\nTimes dispenser was ignored: {}, {:.2f}%\n'.format(s,str(times_used+times_ignored), str(times_used), times_used/(times_used+times_ignored)*100, str(times_ignored), times_ignored/(times_used+times_ignored)*100))