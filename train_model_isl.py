import os, json
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping

# ✅ Settings
DATA_DIR = "dataset"       # your dataset folder
IMG_SIZE = 128             # smaller image size for faster training
BATCH = 32                 # adjust based on memory
EPOCHS = 8                 # reduced epochs for speed

# ✅ Data preprocessing
datagen = ImageDataGenerator(
    rescale=1./255,
    validation_split=0.2,
    rotation_range=10,
    zoom_range=0.1,
    width_shift_range=0.05,
    height_shift_range=0.05,
    horizontal_flip=False
)

train = datagen.flow_from_directory(
    DATA_DIR,
    target_size=(IMG_SIZE, IMG_SIZE),
    batch_size=BATCH,
    subset="training",
    class_mode="categorical"
)

val = datagen.flow_from_directory(
    DATA_DIR,
    target_size=(IMG_SIZE, IMG_SIZE),
    batch_size=BATCH,
    subset="validation",
    class_mode="categorical"
)

# ✅ Base model (transfer learning)
base = MobileNetV2(
    include_top=False,
    weights="imagenet",
    input_shape=(IMG_SIZE, IMG_SIZE, 3)
)
base.trainable = False

x = base.output
x = GlobalAveragePooling2D()(x)
x = Dense(128, activation="relu")(x)   # smaller dense layer
x = Dropout(0.3)(x)
out = Dense(train.num_classes, activation="softmax")(x)

model = Model(base.input, out)

model.compile(
    optimizer=Adam(1e-4),
    loss="categorical_crossentropy",
    metrics=["accuracy"]
)

# ✅ Early stopping to save time
early = EarlyStopping(monitor="val_accuracy", patience=2, restore_best_weights=True)

print("🔥 Training...")
model.fit(train, validation_data=val, epochs=EPOCHS, callbacks=[early])

# ✅ Fine tuning (shorter run)
base.trainable = True
for layer in base.layers[:-30]:
    layer.trainable = False

model.compile(
    optimizer=Adam(1e-5),
    loss="categorical_crossentropy",
    metrics=["accuracy"]
)

print("🔥 Fine-tuning...")
model.fit(train, validation_data=val, epochs=5, callbacks=[early])  # only 5 epochs

# ✅ Save model & labels
os.makedirs("models", exist_ok=True)
model.save("models/sign_model.h5")

with open("models/labels.json", "w") as f:
    json.dump(train.class_indices, f)

# ✅ Final evaluation
loss, acc = model.evaluate(val)
print("✅ Final Validation Accuracy:", acc)