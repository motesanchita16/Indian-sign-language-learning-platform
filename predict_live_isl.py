import cv2
import json
import numpy as np
import mediapipe as mp
import tensorflow as tf
from collections import deque

model = tf.keras.models.load_model("models/sign_model.h5")
with open("models/labels.json") as f:
    labels = {v:k for k,v in json.load(f).items()}

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

history = deque(maxlen=12)
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    h,w,_ = frame.shape
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    res = hands.process(rgb)

    label_text = "No Hand"

    if res.multi_hand_landmarks:
        lm = res.multi_hand_landmarks[0]
        xs = [p.x for p in lm.landmark]
        ys = [p.y for p in lm.landmark]
        x1 = max(0, int(min(xs)*w)-20)
        y1 = max(0, int(min(ys)*h)-20)
        x2 = min(w, int(max(xs)*w)+20)
        y2 = min(h, int(max(ys)*h)+20)

        roi = frame[y1:y2, x1:x2]
        roi = cv2.resize(roi, (224,224))
        roi = roi / 255.0
        roi = np.expand_dims(roi, axis=0)

        pred = model.predict(roi, verbose=0)[0]
        conf = np.max(pred)
        cls = labels[np.argmax(pred)]

        if conf > 0.7:
            history.append(cls)
            if history.count(cls) > 8:
                label_text = cls

        cv2.rectangle(frame, (x1,y1), (x2,y2), (0,255,0), 2)

    cv2.putText(frame, label_text, (30,50),
                cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0,255,0), 3)

    cv2.imshow("ISL Prediction", frame)
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
