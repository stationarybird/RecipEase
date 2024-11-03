import os
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import ResNet50
from tensorflow.keras import layers, models
from tensorflow.keras.optimizers import Adam

train_dir = 'food-101/food-101/food-101/test'
test_dir = 'food-101/food-101/food-101/test'

# Check if the model file already exists
model_path = "food101_model.h5"
if os.path.exists(model_path):
    print("Model already exists. No need to retrain.")
else:
    # Data augmentation
    train_datagen = ImageDataGenerator(rescale=1.0/255.0)
    train_generator = train_datagen.flow_from_directory(
        train_dir,
        target_size=(224, 224),
        batch_size=32,
        class_mode='categorical'
    )

    # Load pre-trained ResNet50 model without the top layer
    base_model = ResNet50(weights='imagenet', include_top=False, input_shape=(224, 224, 3))
    
    # Freeze layers in the base model
    for layer in base_model.layers:
        layer.trainable = False
    
    # Build the model on top of the base model
    model = models.Sequential([
        base_model,
        layers.GlobalAveragePooling2D(),
        layers.Dense(101, activation='softmax')  # 101 classes for Food-101
    ])
    
    # Compile the model
    model.compile(optimizer=Adam(), loss='categorical_crossentropy', metrics=['accuracy'])
    
    # Train the model
    model.fit(train_generator, epochs=10)  # Adjust epochs as needed
    
    # Save the model
    model.save(model_path)
    print("Model training complete and saved as food101_model.h5")