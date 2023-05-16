import tensorflow as tf
import json
import configparser
import os
import sys

config = configparser.ConfigParser()
config.sections()
config.read('rnn/launch.ini')

datasets = [
    'rnn/datasets/recipes_raw_nosource_ar.json',
    'rnn/datasets/recipes_raw_nosource_epi.json',
    'rnn/datasets/recipes_raw_nosource_fn.json',
]

STOP_TITLE = "* "
STOP_INGREDIENTS = "\n---\n\n"
STOP_INSTRUCTIONS = "\n----\n\n"
STOP_RECIPE = "_"

config_model = config['MODEL']

MAX_RECIPE_LENGTH = int(config_model['MAX_RECIPE_LENGTH'])

BATCH_SIZE = int(config_model['BATCH_SIZE'])
SHUFFLE_BUFFER_SIZE = int(config_model['SHUFFLE_NUMBER'])

config_dirs = config['DIRs']

checkpoint_dir = config_dirs['CHECKPOINT_DIR']

# Loading Datasets
final_dataset = []

for dataset in datasets:

    with open(dataset) as f:
        
            loaded_json = json.load(f)
            json_values = list(loaded_json.values())

            final_dataset.extend(json_values)
# ---

# Cleaning Datasets
clean_dataset = []

fields = ['title', 'ingredients', 'instructions']

for recipe in final_dataset:
    
    all_values = True
    
    if not recipe:
        continue

    for field in fields:
        if not recipe[field]:
            all_values = False
        
        if type(recipe[field]) == list and len(recipe[field]) == 0:
            all_values = False

    if all_values:
        clean_dataset.append(recipe)
# ---

# Converting recipe to string
recipes_in_string = []

for recipe in clean_dataset:
    adv = 'ADVERTISEMENT'
    
    title = recipe['title']
    ingredients = recipe['ingredients']
    instructions = recipe['instructions'].split('\n')
    
    ingredients_string = ''
    for ingredient in ingredients:
        ingredient = ingredient.replace(adv, '')
        if ingredient:
            ingredients_string += f'• {ingredient}\n'
    
    instructions_string = ''
    for instruction in instructions:
        instruction = instruction.replace(adv, '')
        if instruction:
            instructions_string += f'▪︎ {instruction}\n'
    
    final_string = STOP_TITLE + str(title) + "\n"
    final_string += STOP_INGREDIENTS + str(ingredients_string)
    final_string += STOP_INSTRUCTIONS + str(instructions_string)
    
    recipes_in_string.append(final_string)
# ---

# Filter
filtered = []
for recipe in recipes_in_string:
    if len(recipe) <= MAX_RECIPE_LENGTH:
        filtered.append(recipe)
# ---


tokenizer = tf.keras.preprocessing.text.Tokenizer(
    lower=False,
    char_level=True,
    filters='',
    split=''
)

tokenizer.fit_on_texts([STOP_RECIPE])
tokenizer.fit_on_texts(filtered)

final_tokenizer = tokenizer
