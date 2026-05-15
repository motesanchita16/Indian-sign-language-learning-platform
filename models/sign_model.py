import json, cv2, numpy as np, mediapipe as mp, tensorflow as tf

class SignLanguageModel:
    def __init__(self,
                 keras_path="models/sign_model.h5",
                 labels_path="models/labels.json"):

        self.model = tf.keras.models.load_model(keras_path)
        print("✅ Keras model loaded")

        with open(labels_path) as f:
            labels = json.load(f)
            self.index_to_label = {v: k for k, v in labels.items()}

        self.input_size = (128, 128)

        self.hands = mp.solutions.hands.Hands(
            static_image_mode=False,
            max_num_hands=2,          # ✅ Two hands
            min_detection_confidence=0.6,
            min_tracking_confidence=0.6
        )

        self.drawer = mp.solutions.drawing_utils
        self.frame_count = 0
        self.skip_frames = 5         # ✅ Predict every 5th frame
        self.last_label = ""

    def preprocess(self, img):
        img = cv2.resize(img, self.input_size)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = img.astype("float32") / 255.0
        return np.expand_dims(img, axis=0)

    def process_frame(self, frame):
        self.frame_count += 1
        frame = cv2.resize(frame, (640, 480))
        annotated = frame.copy()
        h, w, _ = frame.shape

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb)

        label_out = ""

        if results.multi_hand_landmarks:
            for hand in results.multi_hand_landmarks:
                self.drawer.draw_landmarks(
                    annotated, hand, mp.solutions.hands.HAND_CONNECTIONS
                )

            if self.frame_count % self.skip_frames == 0:
                hand = results.multi_hand_landmarks[0]
                xs = [p.x for p in hand.landmark]
                ys = [p.y for p in hand.landmark]

                x1 = max(int(min(xs) * w) - 20, 0)
                y1 = max(int(min(ys) * h) - 20, 0)
                x2 = min(int(max(xs) * w) + 20, w)
                y2 = min(int(max(ys) * h) + 20, h)

                roi = frame[y1:y2, x1:x2]

                if roi.size > 0:
                    img = self.preprocess(roi)
                    preds = self.model.predict(img, verbose=0)[0]
                    idx = int(np.argmax(preds))
                    conf = float(preds[idx])

                    if conf > 0.7:
                        label_out = self.index_to_label.get(idx, "")
                        self.last_label = label_out
                    else:
                        label_out = ""

        if self.last_label:
            cv2.putText(
                annotated,
                self.last_label,
                (10, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.2,
                (0, 255, 0),
                3
            )

        return annotated, label_out
