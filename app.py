from flask import Flask, Response, jsonify
from flask_cors import CORS
import cv2
import mediapipe as mp
import pygame
import threading

app = Flask(__name__)
CORS(app)

pygame.mixer.init()

sounds_mapping = {
    1: "sounds/kick-bass.mp3",
    2: "sounds/crash.mp3",
    3: "sounds/snare.mp3",
    4: "sounds/tom-1.mp3",
    5: "sounds/tom-2.mp3",
    6: "sounds/tom-3.mp3",
    7: "sounds/cr78-Cymbal.mp3",
    8: "sounds/cr78-Guiro 1.mp3",
    9: "sounds/tempest-HiHat Metal.mp3",
    10: "sounds/cr78-Bongo High.mp3"
}

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

cap = cv2.VideoCapture(0)
finger_count = 0
lock = threading.Lock()

def process_video():
    global finger_count
    with mp_hands.Hands(
        model_complexity=0,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5) as hands:
        while True:
            success, image = cap.read()
            if not success:
                continue

            image.flags.writeable = False
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = hands.process(image)
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            count = 0
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    handIndex = results.multi_hand_landmarks.index(hand_landmarks)
                    handLabel = results.multi_handedness[handIndex].classification[0].label
                    handLandmarks = []

                    for landmarks in hand_landmarks.landmark:
                        handLandmarks.append([landmarks.x, landmarks.y])

                    if handLabel == "Left" and handLandmarks[4][0] > handLandmarks[3][0]:
                        count += 1
                    elif handLabel == "Right" and handLandmarks[4][0] < handLandmarks[3][0]:
                        count += 1

                    if handLandmarks[8][1] < handLandmarks[6][1]:
                        count += 1
                    if handLandmarks[12][1] < handLandmarks[10][1]:
                        count += 1
                    if handLandmarks[16][1] < handLandmarks[14][1]:
                        count += 1
                    if handLandmarks[20][1] < handLandmarks[18][1]:
                        count += 1

                    mp_drawing.draw_landmarks(
                        image,
                        hand_landmarks,
                        mp_hands.HAND_CONNECTIONS,
                        mp_drawing_styles.get_default_hand_landmarks_style(),
                        mp_drawing_styles.get_default_hand_connections_style())

            with lock:
                finger_count = count

            if finger_count in sounds_mapping:
                sound_file = sounds_mapping[finger_count]
                pygame.mixer.music.load(sound_file)
                pygame.mixer.music.play()
                if finger_count <= 5:
                    pygame.time.delay(100) 
                elif 5 < finger_count <= 9:
                    pygame.time.delay(100)
                    pygame.mixer.music.play()
                pygame.mixer.music.stop()

            cv2.putText(image, str(finger_count), (50, 450), cv2.FONT_HERSHEY_SIMPLEX, 3, (255, 0, 0), 10)
            _, jpeg = cv2.imencode('.jpg', image)
            frame = jpeg.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(process_video(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/finger_count', methods=['GET'])
def get_finger_count():
    global finger_count
    with lock:
        return jsonify({"finger_count": finger_count})

if __name__ == '__main__':
    app.run(debug=True)
