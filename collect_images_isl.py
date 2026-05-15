import cv2
import mediapipe as mp
import os

label = "A"  # change manually
save_dir = f"dataset/{label}"
os.makedirs(save_dir, exist_ok=True)

cap = cv2.VideoCapture(0)
hands = mp.solutions.hands.Hands(max_num_hands=1)
draw = mp.solutions.drawing_utils

count = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    res = hands.process(rgb)

    if res.multi_hand_landmarks:
        h, w, _ = frame.shape
        lm = res.multi_hand_landmarks[0]

        xs = [p.x for p in lm.landmark]
        ys = [p.y for p in lm.landmark]

        x1, x2 = int(min(xs)*w)-30, int(max(xs)*w)+30
        y1, y2 = int(min(ys)*h)-30, int(max(ys)*h)+30

        x1, y1 = max(x1,0), max(y1,0)
        x2, y2 = min(x2,w), min(y2,h)

        roi = frame[y1:y2, x1:x2]
        if roi.size > 0:
            roi = cv2.resize(roi, (224,224))
            cv2.imshow("ROI", roi)

            key = cv2.waitKey(1)
            if key == ord('s'):
                cv2.imwrite(f"{save_dir}/{count}.jpg", roi)
                count += 1
                print("Saved", count)

    cv2.imshow("Camera", frame)
    if cv2.waitKey(1) == 27:
        break

cap.release()
cv2.destroyAllWindows()
