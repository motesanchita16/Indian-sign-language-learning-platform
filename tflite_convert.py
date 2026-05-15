# tflite_convert.py
import tensorflow as tf
import os

keras_model = "models/sign_model.h5"
tflite_model = "models/sign_model.tflite"

if not os.path.exists(keras_model):
    print("No keras model to convert:", keras_model)
    exit(1)

model = tf.keras.models.load_model(keras_model)
converter = tf.lite.TFLiteConverter.from_keras_model(model)
converter.optimizations = [tf.lite.Optimize.DEFAULT]
# converter.target_spec.supported_types = [tf.float16]  # optional
tflite = converter.convert()
with open(tflite_model, "wb") as f:
    f.write(tflite)
print("Saved tflite:", tflite_model)
