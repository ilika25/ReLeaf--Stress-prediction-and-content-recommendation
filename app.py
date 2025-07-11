from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_session import Session
from pymongo import MongoClient
from dotenv import load_dotenv
from stress_predictor import ( # type: ignore
    calculate_stress_ml, get_stress_label, recommend_content,
    save_data, save_content_feedback, fallback_stress_score
)
from content_library import content_library # type: ignore
from datetime import datetime
import base64
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import cv2
import csv
import os
app = Flask(__name__)
from fer import FER
load_dotenv()
app.secret_key = os.getenv("SECRET_KEY")
mongo_uri = os.getenv("MONGO_URI")

# Flask session configuration
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# MongoDB setup
client = MongoClient(mongo_uri)
db = client["StressPredictor"]
users_collection = db["users"]
stress_collection = db["stress_data"]

@app.route('/')
def home():
    return render_template("home.html")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username= request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        if users_collection.find_one({"email": email}):
            return render_template("register.html", error="❌ Email already registered.")
        users_collection.insert_one({"email": email, "password": password, "username": username})
        return redirect(url_for('login'))
    return render_template("register.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = users_collection.find_one({"email": email})
        if user and check_password_hash(user['password'], password):
            session['user_email'] = email
            session['user_name'] = user['username']
            return redirect(url_for('input_form'))
        else:
            return render_template("login.html", error="❌ Invalid Credentials.")
    return render_template("login.html")

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/input')
def input_form():
    if 'user_email' not in session:
        return redirect(url_for('login'))
    return render_template('input.html', user_email=session['user_email'])

@app.route('/predict', methods=['POST'])
def predict():
    if 'user_email' not in session:
        return redirect(url_for('login'))

    try:
        speed = float(request.form['typing_speed'])
        typos = int(request.form['typos'])
        sleep = float(request.form['sleep'])
        screen = float(request.form['screen'])
        user_type = request.form['user_type']
        user_email = session['user_email']

        expression = "No face detected"
        image_file = request.files.get('image')
        if image_file:
            np_img = np.frombuffer(image_file.read(), np.uint8)
            img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)
            detector = FER(mtcnn=True)
            result = detector.detect_emotions(img)
            if result:
                emotions = result[0]['emotions']
                expression = max(emotions, key=emotions.get)

    except Exception as e:
        return f"❌ Invalid input: {e}"

    try:
        stress_score = calculate_stress_ml(speed, typos, sleep, screen, expression, user_type)
    except:
        stress_score = fallback_stress_score(speed, typos, sleep, screen, expression, user_type)

    label = get_stress_label(stress_score)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # ⏺️ Save prediction to MongoDB before feedback
    stress_collection.insert_one({
        "timestamp": timestamp,
        "user_email": user_email,
        "typing_speed": speed,
        "typos": typos,
        "sleep_hours": sleep,
        "screen_hours": screen,
        "expression": expression,
        "user_type": user_type,
        "stress_score": stress_score,
        "predicted_label": label
    })

    # 📈 Generate graph
    graph_path = generate_user_graph(user_email)
    graph_data = ""
    if graph_path:
        with open(graph_path, "rb") as img_file:
            graph_data = "data:image/png;base64," + base64.b64encode(img_file.read()).decode()

    try:
        recommended_tag = recommend_content(speed, typos, sleep, screen, expression, user_type, stress_score)
        content = content_library.get(recommended_tag, {})
    except:
        recommended_tag = "general"
        content = {}

    return render_template("result.html",
                           speed=speed,
                           typos=typos,
                           sleep=sleep,
                           screen=screen,
                           user_type=user_type,
                           expression=expression,
                           stress_score=stress_score,
                           label=label,
                           tag=recommended_tag,
                           content=content,
                           graph=graph_data,
                           user_email=user_email)

@app.route('/submit-feedback', methods=['POST'])
def submit_feedback():
    if 'user_email' not in session:
        return redirect(url_for('login'))

    try:
        speed = float(request.form['speed'])
        typos = int(request.form['typos'])
        sleep = float(request.form['sleep'])
        screen = float(request.form['screen'])
        user_type = request.form['user_type']
        expression = request.form['expression']
        stress_score = float(request.form['stress_score'])
        tag = request.form['tag']
        user_email = session['user_email']
        user_name = session['user_name']

        actual_stress = float(request.form['actual_stress'])
        accuracy = float(request.form['accuracy'])
        content_feedback = int(request.form['content_feedback'])

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Save to CSV
        save_data([timestamp, speed, typos, sleep, screen, expression, stress_score],
                  actual_stress, accuracy, get_stress_label(stress_score), user_type)
        save_content_feedback([speed, typos, sleep, screen, expression, user_type, stress_score], tag, content_feedback)

        # ❌ No need to insert to MongoDB again (already done in /predict)

        # Generate graph
        graph_path = generate_user_graph(user_email)
        graph_data = ""
        if graph_path:
            with open(graph_path, "rb") as img_file:
                graph_data = "data:image/png;base64," + base64.b64encode(img_file.read()).decode()

        content = content_library.get(tag, {})

        return render_template("result.html",
                               speed=speed,
                               typos=typos,
                               sleep=sleep,
                               screen=screen,
                               user_type=user_type,
                               expression=expression,
                               stress_score=stress_score,
                               label=get_stress_label(stress_score),
                               tag=tag,
                               content=content,
                               graph=graph_data,
                               user_email=user_email,
                               user_name=user_name)

    except Exception as e:
        return f"❌ Error submitting feedback: {e}"

@app.route('/plot/<user_email>')
def plot_user_stress(user_email):
    try:
        graph_url = generate_user_graph(user_email)
        return render_template("user_graph.html", graph_url=graph_url)
    except Exception as e:
        return f"❌ Error generating user graph: {e}"

def generate_user_graph(user_email):
    try:
        user_name = session.get('user_name', user_email)  # fallback to email if name not in session

        records = list(stress_collection.find(
            {"user_email": user_email},
            {"_id": 0, "timestamp": 1, "stress_score": 1}
        ))

        if not records:
            return None

        df = pd.DataFrame(records)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df.sort_values('timestamp', inplace=True)

        plt.figure(figsize=(12, 6))
        plt.plot(df['timestamp'], df['stress_score'], marker='o', linestyle='-', color='teal')
        plt.xlabel("Timestamp")
        plt.ylabel("Stress Score")
        plt.title(f"Stress Trend for {user_name}")
        plt.xticks(rotation=45)
        plt.tight_layout()

        filename = f"static/graph_{user_email}.png"
        plt.savefig(filename)
        plt.close()

        return filename

    except Exception as e:
        print(f"Graph generation error: {e}")
        return None

if __name__ == "__main__":
    if not os.path.exists("content_training.csv"):
        with open("content_training.csv", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["typing_speed", "typos", "sleep_hours", "screen_hours",
                             "expression", "user_type", "stress_score",
                             "content_tag", "content_feedback"])

    app.run(debug=True)
