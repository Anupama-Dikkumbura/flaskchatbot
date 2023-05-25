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
    global user_id
    connection = sqlite3.connect(current_directory + "/database.db")
    cursor = connection.cursor()
    query = "SELECT gpa FROM users WHERE esoftid=?"
    result = cursor.execute(query, (user_id,))
    gpa = result.fetchone()
    print(gpa)

    if gpa[0] is not None:
        send("Your GPA is " + str(gpa[0]), broadcast=True)
    else:
        send("GPA not found for user with ID: " + user_id, broadcast=True)

    connection.close()


def get_courses():
    global user_id
    connection = sqlite3.connect(current_directory + "/database.db")
    cursor = connection.cursor()

    query = "SELECT course FROM user_courses WHERE esoftid=?"
    result = cursor.execute(query, (user_id,))
    courses = result.fetchall()

    if courses:
        course_names = "|".join([course[0] for course in courses])
        send("You are currently enrolled in the following courses:|" + course_names, broadcast=True)
    else:
        send("You are not currently enrolled in any courses.", broadcast=True)
    # Close the database connection
    connection.close()


def get_tasks():
    global user_id
    connection = sqlite3.connect(current_directory + "/database.db")
    cursor = connection.cursor()

    query = "SELECT task, course, deadline FROM tasks WHERE esoftid=?"
    result = cursor.execute(query, (user_id,))
    tasks = result.fetchall()

    if tasks:
        task_sentences = []
        for task in tasks:
            task_sentence = " >> ".join(task)
            task_sentences.append(task_sentence)
        tasks_combined = " | ".join(task_sentences)
        send("You are currently enrolled in the following tasks:|" + tasks_combined, broadcast=True)
    else:
        send("You are not currently enrolled in any tasks.", broadcast=True)

    # Close the database connection
    connection.close()


def login(loginData):
    global is_logged_in
    global user_id
    global password
    global current_directory
    global recent_tag

    user_id = loginData['userId']
    password = loginData['password']

    connection = sqlite3.connect(current_directory + "/database.db")
    cursor = connection.cursor()

    query = "SELECT * FROM users WHERE esoftid='{n}' AND password='{m}'".format(n=user_id, m=password)
    result = cursor.execute(query)
    user = cursor.fetchone()  # Retrieve the first row from the result

    if user is not None:
        is_logged_in = True
        send("Login successful.", broadcast=True)
        if recent_tag == "gpa":
            recent_tag = ""
            get_gpa()
        elif recent_tag == "courses":
            recent_tag = ""
            get_courses()
        elif recent_tag == "tasks_deadlines":
            recent_tag = ""
            get_tasks()
        print("Login successful.")
    else:
        is_logged_in = False
        user_id = ""
        password = ""
        send("Username and Password do not match!. Try Again!", broadcast=True)
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

    if message != "User connected!":
        if not isinstance(message, str):
            login(message)
        elif message == "Logout" or message == "logout":
            is_logged_in = False
            user_id = ""
            password = ""
            recent_tag = ""
            send("Logged out successfully! Anything else I can assist you with", broadcast=True)
        else:
            ints = predict_class(message)
            if ints[0]['intent'] == "gpa":
                if is_logged_in:
                    get_gpa()
                else:
                    recent_tag = "gpa"
                    send("You have to login first", broadcast=True)
            elif ints[0]['intent'] == "courses":
                if is_logged_in:
                    get_courses()
                else:
                    recent_tag = "courses"
                    send("You have to login first", broadcast=True)
            elif ints[0]['intent'] == "tasks_deadlines":
                if is_logged_in:
                    get_tasks()
                else:
                    recent_tag = "tasks_deadlines"
                    send("You have to login first", broadcast=True)
            elif ints[0]['intent'] == "notfound":
                send("I'm sorry, but I'm unable to understand the message '" +
                     message +
                     "' If you have a specific question or if there's something specific you'd "
                     "like to discuss, please let me know, and I'll be glad to assist you.", broadcast=True)

            else:
                res = get_response(ints, intents)
                send(res, broadcast=True)


@app.route('/')
def index():
    return render_template("index.html")


if __name__ == "__main__":
    socketio.run(app, host="localhost", allow_unsafe_werkzeug=True)