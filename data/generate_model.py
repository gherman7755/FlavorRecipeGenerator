import tensorflow as tf
import os
from recipe_generator import model, SHUFFLE_NUMBER, BATCH_SIZE
from recipe_tokenizer import final_tokenizer as tokenizer
from recipe_tokenizer import filtered, MAX_RECIPE_LENGTH, STOP_RECIPE


dataset_vectorized = tokenizer.texts_to_sequences(filtered)

dataset_vectorized_padded_without_stops = tf.keras.preprocessing.sequence.pad_sequences(
    dataset_vectorized,
    padding='post',
    truncating='post',
    maxlen=MAX_RECIPE_LENGTH-1,
    value=tokenizer.texts_to_sequences([STOP_RECIPE])[0]
)

dataset_vectorized_padded = tf.keras.preprocessing.sequence.pad_sequences(
    dataset_vectorized_padded_without_stops,
    padding='post',
    truncating='post',
    maxlen=MAX_RECIPE_LENGTH+1,
    value=tokenizer.texts_to_sequences([STOP_RECIPE])[0]
)


dataset = tf.data.Dataset.from_tensor_slices(dataset_vectorized_padded)

def split_input_target(recipe):
    input_text = recipe[:-1]
    target_text = recipe[1:]
    
    return input_text, target_text

dataset_targeted = dataset.map(split_input_target)

dataset_train = dataset_targeted.shuffle(SHUFFLE_NUMBER).batch(BATCH_SIZE, drop_remainder=True).repeat()

def loss(labels, logits):
    entropy = tf.keras.losses.sparse_categorical_crossentropy(
      y_true=labels,
      y_pred=logits,
      from_logits=True
    )
    
    return entropy

adam_optimizer = tf.keras.optimizers.Adam(learning_rate=0.001)

model.compile(
    optimizer=adam_optimizer,
    loss=loss
)

early_stopping_callback = tf.keras.callbacks.EarlyStopping(
    patience=5,
    monitor='loss',
    restore_best_weights=True,
    verbose=1
)

checkpoint_dir = 'data/tmp/checkpoints'
os.makedirs(checkpoint_dir, exist_ok=True)

checkpoint_prefix = os.path.join(checkpoint_dir, 'ckpt_{epoch}')
checkpoint_callback=tf.keras.callbacks.ModelCheckpoint(
    filepath=checkpoint_prefix,
    save_weights_only=True
)

EPOCHS = 2
INITIAL_EPOCH = 0
STEPS_PER_EPOCH = 4

history = model.fit(x=dataset_train, epochs=EPOCHS, steps_per_epoch=STEPS_PER_EPOCH, initial_epoch=INITIAL_EPOCH,
    callbacks=[
        checkpoint_callback,
        early_stopping_callback
    ]
)

model_name = 'generation3.h5'
model.save(model_name, save_format='h5')