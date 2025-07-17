# stress_predictor.py
import cv2
import time
import random
import csv
import joblib
import numpy as np
import matplotlib.pyplot as plt
from fer import FER
from datetime import datetime
import joblib
import numpy as np
import os
from .content_library import content_library

# ----------- Phase 1: Typing Speed & Typos -----------
def measure_typing():
    sentences = [
        "The quick brown fox jumps over the lazy dog.",
        "Debugging is like being the detective in a crime movie.",
        "Simplicity is the soul of efficiency.",
        "A bug in the code is worth two in production.",
        "Great code is its own best documentation."
    ]
    target = random.choice(sentences)
    print(f"Type the following sentence:\n\{target}")
    input("Press Enter when you're ready...")
    start = time.time()
    typed = input("Start typing here:\n")
    end = time.time()

    time_taken = end - start
    target_words = target.strip().split()
    typed_words = typed.strip().split()
    typo_count = sum(1 for t, u in zip(target_words, typed_words) if t != u) #typos due to incorrect words
    typo_count += abs(len(typed_words) - len(target_words)) #typos due to mismatch in length i.e lesser/more no. of words
    correct_words = max(len(target_words) - typo_count, 0)
    wpm = (correct_words / time_taken) * 60 if time_taken > 0 else 0

    print("\nResults:")
    print(f"Time taken: {time_taken:.2f} seconds")
    print(f"Typing speed: {wpm:.2f} words per minute (WPM)")
    print(f"Typos (by word): {typo_count}")

    return wpm, typo_count

# ----------- Phase 2: Capture & Detect Expression -----------
def capture_frame():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Webcam could not be accessed.")
        return None
    print("Press 'c' to capture a frame, or 'q' to quit.")
    frame = None
    while True:
        ret, live_frame = cap.read()
        if not ret:
            print("Failed to capture frame.")
            break
        cv2.imshow("Live Feed - Press 'c' to capture", live_frame)
        key = cv2.waitKey(1)
        if key == ord('c'):
            frame = live_frame.copy()
            print("Frame captured!")
            break
        elif key == ord('q'):
            print("Capture cancelled.")
            break
    cap.release()
    cv2.destroyAllWindows()
    return frame

def detect_expression():
    frame = capture_frame()
    if frame is None:
        return "No face detected"
    detector = FER(mtcnn=True)
    result = detector.detect_emotions(frame)
    if not result:
        print("No face detected.")
        return "No face detected"
    for face in result:
        (x, y, w, h) = face["box"]
        emotions = face["emotions"]
        top_emotion = max(emotions, key=emotions.get)
        confidence = emotions[top_emotion]
        label = f"{top_emotion} ({confidence:.2f})"
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
    cv2.imshow("Face with Emotion", frame)
    cv2.waitKey(3000)
    cv2.destroyAllWindows()
    return top_emotion

# ----------- Phase 3: ML Stress Prediction -----------

import os
import joblib
import pandas as pd

def calculate_stress_ml(speed, typos, sleep, screen, expression, user_type):
    # Fallback to rule-based method if model not available
    model_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models")
    stress_model_path= os.path.join(model_folder,"stress_model.pkl")
    label_encoder_expression_path= os.path.join(model_folder,"label_encoder_expression.pkl")
    label_encoder_user_path= os.path.join(model_folder,"label_encoder_user_type.pkl")
    if not os.path.exists(stress_model_path) or \
       not os.path.exists(label_encoder_expression_path) or \
       not os.path.exists(label_encoder_user_path):
        print("\n⚠️ Model not trained yet. Using basic rule-based estimation.\n")
        return fallback_stress_score(speed, typos, sleep, screen, expression, user_type)

    # Load model and encoders
    model = joblib.load("../models/stress_model.pkl")
    le_expression = joblib.load("../models/label_encoder_expression.pkl")
    le_user_type = joblib.load("../models/label_encoder_user_type.pkl")

    # Encode categorical inputs
    expression_encoded = le_expression.transform([expression])[0]
    user_type_encoded = le_user_type.transform([user_type])[0]

    # Prepare input for prediction
    input_data = pd.DataFrame([{
        "typing_speed": speed,
        "typos": typos,
        "sleep_hours": sleep,
        "screen_hours": screen,
        "expression_encoded": expression_encoded,
        "user_type_encoded": user_type_encoded
    }])

    # Predict
    prediction = model.predict(input_data)[0]

    print("\n✅ Prediction completed using trained model.")
    print(f"📈 Predicted Stress Level: {round(prediction, 2)}")

    return round(prediction, 2)

def get_user_type():
    print("\nSelect your profile type:")
    print("1. Student")
    print("2. Professional")
    print("3. Gamer")
    print("4. Casual User")
    choice = input("Enter the number corresponding to your type: ").strip()

    mapping = {
        "1": "student",
        "2": "professional",
        "3": "gamer",
        "4": "casual"
    }

    selected = mapping.get(choice, "student")  # default fallback
    print(f"You selected: {selected.title()} profile.\n")
    return selected

def get_screen_stress(screen_hours, user_type="student"):
    if user_type == "student":
        if screen_hours <= 5:
            return 0
        elif screen_hours <= 7:
            return 10
        elif screen_hours <= 10:
            return 15
        elif screen_hours <= 12:
            return 20
        else:
            return 25

    elif user_type == "professional":
        if screen_hours <= 5:
            return 0
        elif screen_hours <= 8:
            return 10
        elif screen_hours <= 11:
            return 15
        elif screen_hours <= 13:
            return 20
        else:
            return 25

    elif user_type == "gamer":
        if screen_hours <= 6:
            return 0
        elif screen_hours <= 9:
            return 10
        elif screen_hours <= 12:
            return 15
        elif screen_hours <= 14:
            return 20
        else:
            return 25

    elif user_type == "casual":
        if screen_hours <= 3:
            return 0
        elif screen_hours <= 5:
            return 10
        elif screen_hours <= 7:
            return 15
        elif screen_hours <= 9:
            return 20
        else:
            return 25

    return 15  # fallback
def get_typing_stress(typing_speed, user_type="student"):
    if user_type == "student":
        if 30 <= typing_speed <= 60:
            return 0
        elif 25 <= typing_speed < 30 or 60 < typing_speed <= 70:
            return 10
        elif 20 <= typing_speed < 25 or 70 < typing_speed <= 80:
            return 15
        elif 15 <= typing_speed < 20 or 80 < typing_speed <= 90:
            return 20
        else:
            return 25

    elif user_type == "professional":
        if 40 <= typing_speed <= 80:
            return 0
        elif 35 <= typing_speed < 40 or 80 < typing_speed <= 90:
            return 10
        elif 30 <= typing_speed < 35 or 90 < typing_speed <= 100:
            return 15
        elif 25 <= typing_speed < 30 or 100 < typing_speed <= 110:
            return 20
        else:
            return 25

    elif user_type == "gamer":
        if 50 <= typing_speed <= 90:
            return 0
        elif 45 <= typing_speed < 50 or 90 < typing_speed <= 100:
            return 10
        elif 40 <= typing_speed < 45 or 100 < typing_speed <= 110:
            return 15
        elif 35 <= typing_speed < 40 or 110 < typing_speed <= 120:
            return 20
        else:
            return 25

    elif user_type == "casual":
        if 20 <= typing_speed <= 40:
            return 0
        elif 15 <= typing_speed < 20 or 40 < typing_speed <= 50:
            return 10
        elif 10 <= typing_speed < 15 or 50 < typing_speed <= 60:
            return 15
        elif 5 <= typing_speed < 10 or 60 < typing_speed <= 70:
            return 20
        else:
            return 25

    return 15  # Default/fallback  
def get_sleep_stress(sleep_hours, user_type="student"):
    if user_type == "student":
        if 6 <= sleep_hours <= 8:
            return 0
        elif 5 <= sleep_hours < 6 or 8 < sleep_hours <= 9:
            return 10
        elif 4 <= sleep_hours < 5 or 9 < sleep_hours <= 10:
            return 15
        elif 3 <= sleep_hours < 4 or 10 < sleep_hours <= 11:
            return 20
        else:
            return 25

    elif user_type == "professional":
        if 6 <= sleep_hours <= 8:
            return 0
        elif 5 <= sleep_hours < 6 or 8 < sleep_hours <= 9:
            return 10
        elif 4 <= sleep_hours < 5 or 9 < sleep_hours <= 10:
            return 15
        elif 3 <= sleep_hours < 4 or 10 < sleep_hours <= 11:
            return 20
        else:
            return 25

    elif user_type == "gamer":
        if 6 <= sleep_hours <= 8:
            return 0
        elif 5 <= sleep_hours < 6 or 8 < sleep_hours <= 9:
            return 10
        elif 4 <= sleep_hours < 5 or 9 < sleep_hours <= 10:
            return 15
        elif 3 <= sleep_hours < 4 or 10 < sleep_hours <= 11:
            return 20
        else:
            return 25

    elif user_type == "casual":
        if 6 <= sleep_hours <= 8:
            return 0
        elif 5 <= sleep_hours < 6 or 8 < sleep_hours <= 9:
            return 10
        elif 4 <= sleep_hours < 5 or 9 < sleep_hours <= 10:
            return 15
        elif 3 <= sleep_hours < 4 or 10 < sleep_hours <= 11:
            return 20
        else:
            return 30

    return 15  # fallback if unknown user_type
    
def fallback_stress_score(speed, typos, sleep, screen, expression,user_type="student"):
    # Typing speed (realistic)
    speed_score= get_typing_stress(speed,user_type)
    # Typos (cap at 20 typos)
    typos_score = min(typos, 20) * 1.5  # up to 30

    # Sleep: ideal 8 hrs
    sleep_score = get_sleep_stress(sleep,user_type)  # up to 30

    # Screen time: ideal up to 4 hrs
    screen_score = get_screen_stress(screen, user_type) # up to 32

    # Emotion mapping (stronger influence)
    emotion_map = {
        "angry": 35,
        "disgust": 30,
        "fear": 40,
        "sad": 30,
        "neutral": 10,
        "surprise": 5,
        "happy": 0,
        "No face detected": 15
    }
    emotion_score = emotion_map.get(expression, 20)

    # Combine all
    stress = speed_score + typos_score + sleep_score + screen_score + emotion_score

    return round(min(stress, 100), 2)  # cap at 100



def get_stress_label(score):
    if score <= 20:
        return "Very Low Stress"
    elif score <= 40:
        return "Low Stress"
    elif score <= 60:
        return "Moderate Stress"
    elif score <= 80:
        return "High Stress"
    else:
        return "Extreme Stress"

# ----------- Phase 4: Save Data & Graph -----------
def save_data(data, user_feedback=None, accuracy_feedback=None, label="", user_type="student"):
    filename="user_feedback_data.csv"
    header = [
        "timestamp", "typing_speed", "typos", "sleep_hours", "screen_hours",
        "expression", "user_type", "stress_score", "stress_label",
        "user_stress_feedback", "predicted_accuracy_feedback"
    ]
    try:
        with open(filename, "x", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(header)
    except FileExistsError:
        pass

    # Insert label between stress_score and feedbacks
    with open(filename, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(data[:6] + [user_type] + data[6:] + [label, user_feedback, accuracy_feedback])
def save_content_feedback(features, content_tag, content_feedback):
    filename="content_training_data.csv"
    header = [
        "typing_speed", "typos", "sleep_hours", "screen_hours",
        "expression", "user_type", "stress_score",
        "content_tag", "content_feedback"
    ]
    try:
        with open(filename, "x", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(header)
    except FileExistsError:
        pass
    with open(filename, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(features + [content_tag, content_feedback])

def recommend_content(speed, typos, sleep, screen, expression, user_type, stress_score):
    # Load model and encoders
    base_dir = os.path.dirname(os.path.dirname(__file__))
    model_folder = os.path.join(base_dir, "models")
    model_path= os.path.join(model_folder,"content_recommender_model.pkl")
    encoder_path= os.path.join(model_folder,"label_encoders.pkl")
    model = joblib.load(model_path)
    encoders = joblib.load(encoder_path)

    # Encode categorical values
    expression_encoded = encoders["expression"].transform([expression])[0]
    user_type_encoded = encoders["user_type"].transform([user_type])[0]

    # Prepare input
    features = np.array([[speed, typos, sleep, screen, expression_encoded, user_type_encoded, stress_score]])

    # Predict
    prediction = model.predict(features)[0]
    return prediction

import pandas as pd


def plot_stress(return_path=False):
    try:
        df = pd.read_csv("../utils/user_feedback_data.csv")
        timestamps = df['timestamp']
        stress_scores = df['stress_score']

        # Increase figure size more
        plt.figure(figsize=(18, 6))  # Wider but not too tall

        # Plotting
        plt.plot(timestamps, stress_scores, marker='o', color='royalblue', linewidth=2)

        # Rotate x-ticks and adjust font
        plt.xticks(rotation=45, ha='right', fontsize=10)
        plt.yticks(fontsize=10)

        # Labeling
        plt.title("Stress Score Over Time", fontsize=14, pad=15)
        plt.xlabel("Time", fontsize=12, labelpad=10)
        plt.ylabel("Stress Score", fontsize=12, labelpad=10)

        # Grid and layout
        plt.grid(True, linestyle='--', alpha=0.5)
        plt.tight_layout(pad=4)

        # Save to static folder
        output_path = "static/stress_plot.png"
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()

        if return_path:
            return output_path

    except Exception as e:
        print("❌ Plotting failed:", e)

# ----------- Main Flow -----------
def main():
    speed, typos = measure_typing()
    sleep = float(input("Enter last night's sleep duration (hours): "))
    screen = float(input("Enter your average daily screen time (hours): "))
    user_type = get_user_type()
    expression = detect_expression()
    stress_score = calculate_stress_ml(speed, typos, sleep, screen, expression,user_type)
    label = get_stress_label(stress_score)

    print(f"\n\U0001F4CA Your Stress Score: {stress_score}% – {label}")
    print(f"Typing Speed: {speed:.2f} WPM | Typos: {typos} | Emotion: {expression}")
    recommended_tag = recommend_content(speed, typos, sleep, screen, expression, user_type, stress_score)
    print(f"\n🎯 Recommended Content Category: {recommended_tag}")
    if recommended_tag in content_library:
        content = content_library[recommended_tag]
        print(f"\n📚 Description: {content['description']}")

        if content.get("songs"):
            print("\n🎵 Songs:")
            for s in content["songs"]:
                print(f"  - {s}")

        if content.get("blogs"):
            print("\n📝 Blogs:")
            for b in content["blogs"]:
                print(f"  - {b}")

        if content.get("movies"):
            print("\n🎬 Movies:")
            for m in content["movies"]:
                print(f"  - {m}")

        if content.get("help_sites"):
            print("\n🌐 Help Sites:")
            for h in content["help_sites"]:
                print(f"  - {h}")

        if content.get("hotlines"):
            print("\n☎️ Hotlines:")
            for num in content["hotlines"]:
                print(f"  - {num}")
    else:
        print("⚠️ No content found for this category.")

    try:
        actual_stress = float(input("On a scale of 1 to 10, how stressed do you *actually* feel? "))
    except:
        actual_stress = ""

    try:
        model_accuracy = float(input("On a scale of 1 to 10, how accurate was this prediction? "))
    except:
        model_accuracy = ""
    try:
        feedback_input = input(f"Was the content '{recommended_tag}' helpful? (y/n): ").strip().lower()
        content_feedback = 1 if feedback_input == 'y' else 0
    except:
        content_feedback = 0
    features = [speed, typos, sleep, screen, expression, user_type, stress_score]
    save_content_feedback(features, recommended_tag, content_feedback)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data = [timestamp, speed, typos, sleep, screen, expression, stress_score]
    save_data(data, actual_stress, model_accuracy, label,user_type)
    plot_stress()

if __name__ == "__main__":
    main()