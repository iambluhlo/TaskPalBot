import mysql.connector

API_KEY = ''

bot_db = mysql.connector.connect(
    host="localhost",
    user="ali",
    password="1234",
    database="taskpalbot"
)
