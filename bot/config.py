import mysql.connector

API_KEY = '7567134299:AAEWLM6yglAQEbRqaQTab2EtlExmR7O-Gyc'

bot_db = mysql.connector.connect(
    host="localhost",
    user="ali",
    password="1234",
    database="taskpalbot"
)
