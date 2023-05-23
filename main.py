from flask import Flask, render_template
from flask_socketio import SocketIO, send
from utils import predict_class, get_response
import json
import sqlite3
import os
import pickle
from nltk.stem import WordNetLemmatizer
import tensorflow as tf

# Setting up Database
current_directory = os.path.dirname(os.path.abspath(__file__))

lemmatizer = WordNetLemmatizer()
intents = json.loads(open("intents.json").read())

words = pickle.load(open('words.pkl', 'rb'))
classes = pickle.load(open('classes.pkl', 'rb'))
model = tf.keras.models.load_model('chatbot_model.h5')

# Login status
is_logged_in = False
user_id = ""
password = ""
recent_tag = ""


def get_gpa():
    return "Your GPA: 3.5"


def login():
    print("Login")
    global is_logged_in
    global user_id
    global password
    global current_directory

    connection = sqlite3.connect(current_directory + "/database.db")
    cursor = connection.cursor()

    query = "SELECT * FROM users WHERE esoftid='{n}' AND password='{m}'".format(n=user_id, m=password)
    result = cursor.execute(query)
    user = cursor.fetchone()  # Retrieve the first row from the result

    if user is not None:
        is_logged_in = True
        print("Login successful.")
    else:
        is_logged_in = False
        print("Invalid username or password.")

    cursor.close()
    connection.close()


app = Flask(__name__)
app.config['SECRET_KEY'] = "secret!123"
socketio = SocketIO(app, cors_allowed_origins="*")


@socketio.on('message')
def handle_message(message):
    global is_logged_in
    global user_id
    global password
    global recent_tag
    print("Received message: " + message)

    # check user has entered username or password
    message_parse = message[-3:]

    print(message_parse)
    if message != "User connected!":
        if message_parse == "uid":
            if is_logged_in:
                send("How can I help you?", broadcast=True)
            else:
                user_id = message[:-3]
                send("Enter your password", broadcast=True)
        elif message_parse == "pwd":
            password = message[:-3]
            login()
            if is_logged_in:
                send("You have successfully Logged In", broadcast=True)
                print(recent_tag)
                if recent_tag == "gpa":
                    send(get_gpa(),broadcast=True)
            else:
                user_id = ""
                password = ""
                send("Wrong credentials, enter username again! ", broadcast=True)
        elif message == "Cancel" or message == "cancel":
            is_logged_in = False
            user_id = ""
            password = ""
            recent_tag = ""
            send("Cancelled! Anything else I can assist you with", broadcast=True)
        else:
            ints = predict_class(message)
            if ints[0]['intent'] == "gpa":
                if is_logged_in:
                    res = get_gpa()
                    send(res, broadcast=True)
                else:
                    recent_tag = "gpa"
                    send("You have to login first", broadcast=True)
                    send("Enter Your Username", broadcast=True)
            else:
                res = get_response(ints, intents)
                send(res, broadcast=True)


@app.route('/')
def index():
    return render_template("index.html")


if __name__ == "__main__":
    socketio.run(app, host="localhost", allow_unsafe_werkzeug=True)