import tensorflow as tf
import json
import numpy as np
from recipe_tokenizer import final_tokenizer as tokenizer
import configparser
import os


config = configparser.ConfigParser()
config.read('data/launch.ini')

config_model = config['MODEL']

MAX_RECIPE_LENGTH = config_model['MAX_RECIPE_LENGTH']

STOP_TITLE = "* "
STOP_INGREDIENTS = "\n---\n\n"
STOP_INSTRUCTIONS = "\n----\n\n"
STOP_RECIPE = "_"

# BATCH_SIZE = config_model['BATCH_SIZE']
SHUFFLE_NUMBER = int(config_model['SHUFFLE_NUMBER'])

config_dirs = config['DIRs']

checkpoint_dir = config_dirs['CHECKPOINT_DIR']

BATCH_SIZE = 1
VOCABULARY_SIZE = len(tokenizer.word_counts) + 1

# Creating Model
model = tf.keras.models.Sequential()

model.add(tf.keras.layers.Embedding(
    input_dim=VOCABULARY_SIZE,
    output_dim=256,
    batch_input_shape=[BATCH_SIZE, None]
))

model.add(tf.keras.layers.LSTM(
    units=1024,
    return_sequences=True,
    stateful=True,
    recurrent_initializer=tf.keras.initializers.GlorotNormal()
))

model.add(tf.keras.layers.Dense(VOCABULARY_SIZE))

# checkpoint = tf.train.Checkpoint(model)
# checkpoint_manager = tf.train.CheckpointManager(checkpoint, checkpoint_dir, max_to_keep=7)

# latest_checkpoint = checkpoint_manager.latest_checkpoint
# if latest_checkpoint:
#     checkpoint.restore(latest_checkpoint)

# print(os.listdir(checkpoint_dir))

# .expect_partial()

print("Loading Weights...")

model.load_weights(tf.train.latest_checkpoint(checkpoint_dir))
model.build(tf.TensorShape([BATCH_SIZE, None]))

print("Model Builded...")
# model.summary()

# Generating Recipes
def generate_recipe(model, start_string, num_generate = 800, temperature=1.0):
  
    start_string = STOP_TITLE + start_string
    res_sequence = np.array(tokenizer.texts_to_sequences([start_string]))

    final_recipe = []
    model.reset_states()
    for _ in range(num_generate):
        predictions = model(res_sequence)

        batched_predictions = tf.squeeze(predictions, 0)
        final_predictions = batched_predictions / temperature
        pred_index = tf.random.categorical(final_predictions, num_samples=1)[-1, 0].numpy()

        res_sequence = tf.expand_dims([pred_index], 0)
        next_character = tokenizer.sequences_to_texts(res_sequence.numpy())[0]
        final_recipe.append(next_character)

    return (start_string + ''.join(final_recipe))


def generate_combinations(model, temperature):
    chars_number = 1000
    start_words = ["Apple", "Mushrooms", "Juice"]
    
    for word in start_words:
        print("Generating recipe for: " + word)
        generated_text = generate_recipe(model, word, chars_number, temperature)
        print(generated_text)
            
generate_combinations(model, 0.2)