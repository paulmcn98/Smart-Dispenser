import mysql.connector

#connect to mysql
mydb = mysql.connector.connect(
	host="localhost",
	user="root",
	passwd="intragroup16"
)
mycursor = mydb.cursor()

#Create the dispenser database
mycursor.execute("CREATE DATABASE dispenserdb")