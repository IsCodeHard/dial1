from flask_bootstrap import Bootstrap5
from flask import Flask, render_template, url_for
import pymysql.cursors
from keys import *
import asyncio
from pyami_asterisk import AMIClient

app=Flask(__name__)

bootstrap = Bootstrap5(app)

connection = pymysql.connect(host=MY_SQL_HOST,
                             user=MY_SQL_USER,
                             password=MY_SQL_PASSWORD,
                             database=MY_SQL_DB,
                             cursorclass=pymysql.cursors.DictCursor)

def callback_originate(events):
    print(events)

@app.route('/')
def home():
    with connection.cursor() as cursor:
        # Read a single record
        sql = "SELECT * FROM `users`"
        cursor.execute(sql)
        result = cursor.fetchall()
        
    return render_template('index.html', users=result)

@app.route('/call/<phone>', methods=['POST'])
def dial(phone):
    with connection.cursor() as cursor:
        # Read a single record
        sql = "SELECT * FROM `users` WHERE phone=%s"
        cursor.execute(sql, (phone,))
        result = cursor.fetchone()
        
        if result:
            ami = AMIClient(host=MY_AMI_HOST, port=MY_AMI_PORT, username=MY_AMI_USERNAME, secret=MY_AMI_SECRET)
            ami.create_action(
                {
                    "Action": "Originate",
                    "Channel": "SIP/phone-1",
                    "Timeout": "20000",
                    "CallerID": result['fullname'],
                    "Exten": "500",
                    "Context": MY_AMI_CONTEXT,
                    "Priority": "1",
                },
                callback_originate,
            )
            ami.connect()
            return f"Dial to {result['fullname']}"
        else:
            return "Invalid number"

if __name__ == '__main__':
    app.run()    