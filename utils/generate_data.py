import random
import pandas as pd
user_types = ["student", "professional", "gamer", "casual"]
expressions = ["angry", "disgust", "fear", "sad", "neutral", "surprise", "happy", "No face detected"]
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

# Generate synthetic samples
def generate_synthetic_data(samples=5000, low_stress_min=2000):
    data = []
    low_stress_count = 0

    while len(data) < samples:
        user_type = random.choice(user_types)
        expression = random.choice(expressions)
        typing_speed = random.randint(10, 120)
        typos = random.randint(0, 15)
        sleep = round(random.uniform(1, 11), 1)
        screen = round(random.uniform(0.5, 16), 1)

        stress = fallback_stress_score(typing_speed, typos, sleep, screen, expression, user_type)

        # Ensure enough low-stress samples (<30)
        if stress < 30 and low_stress_count < low_stress_min:
            low_stress_count += 1
        elif low_stress_count >= low_stress_min or stress >= 30:
            pass
        else:
            continue

        data.append({
            "typing_speed": typing_speed,
            "typos": typos,
            "sleep_hours": sleep,
            "screen_hours": screen,
            "expression": expression,
            "user_type": user_type,
            "stress_level": stress
        })

    return pd.DataFrame(data)

# Generate and save to CSV
df = generate_synthetic_data()
df.to_csv("synthetic_stress_data.csv", index=False)
print("✅ synthetic_stress_data.csv generated successfully.")