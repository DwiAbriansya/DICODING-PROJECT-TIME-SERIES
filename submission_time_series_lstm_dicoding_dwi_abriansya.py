# -*- coding: utf-8 -*-
"""Submission Time Series LSTM Dicoding - Dwi Abriansya.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1HuOvo1OJZBKYBawNapJlMXkHtaARRAve

Nama              : Dwi Abriansya Alimuddin

No Registrasi FGA : 0182180121-127

# Submission Time Series LSTM Dicoding

## Import Modul
"""

import numpy as np
import pandas as pd
from keras.layers import Dense, LSTM
import matplotlib.pyplot as plt
import tensorflow as tf

"""## Upload dan Read Dataset"""

# Upload Dataset
from google.colab import files
uploaded = files.upload()

# Read Dataset
df = pd.read_csv('AABA_2006-01-01_to_2018-01-01.csv')
df.head()

"""## Data Preprocessing"""

df.info()

# Missing Value
df.isnull().sum()

"""## Data Visualization"""

# Ekstrak data tanggal dan open
dates = df['Date'].values
open = df['Open'].values
 
# Plot data tanggal dan open
plt.figure(figsize=(20,10))
plt.plot(dates, open)
plt.title('AABA Open Values',
          fontsize=20);

"""## Train Test Split

### Split Data
"""

# Split Data Train dan Test dengan Rasio 80:20, Shuffle=False agar split data tidak random
from sklearn.model_selection import train_test_split
date_latih, date_test, open_latih, open_test = train_test_split(dates, open, test_size=0.2, shuffle=False)

"""### Persiapan Train dan Test Set"""

# Inisiasi Fungsi windowed dataset
def windowed_dataset(series, window_size, batch_size, shuffle_buffer):
    series = tf.expand_dims(series, axis=-1)
    ds = tf.data.Dataset.from_tensor_slices(series)
    ds = ds.window(window_size + 1, shift=1, drop_remainder=True)
    ds = ds.flat_map(lambda w: w.batch(window_size + 1))
    ds = ds.shuffle(shuffle_buffer)
    ds = ds.map(lambda w: (w[:-1], w[-1:]))
    return ds.batch(batch_size).prefetch(1)

# Memanggil fungsi windowed dataset
train_set = windowed_dataset(open_latih, window_size=60, batch_size=100, shuffle_buffer=1000)
test_set = windowed_dataset(open_test, window_size=60, batch_size=100, shuffle_buffer=1000)

"""## Arsitektur Model"""

# Arsitektur Model
model = tf.keras.models.Sequential([
  # LSTM layer 1
  tf.keras.layers.LSTM(60, return_sequences=True),
  # LSTM layer 2
  tf.keras.layers.LSTM(60),
  # Hidden Layer 1
  tf.keras.layers.Dense(30, activation="relu"),
  # Hidden Layer 2
  tf.keras.layers.Dense(10, activation="relu"),
  # Output Layer
  tf.keras.layers.Dense(1),
])

"""## Threshold dan Callback

### Penentuan Threshold
"""

# Skala Data
skala = np.max(df['Open'])-np.min(df['Open'])

# Threshold MAE
threshold = skala*0.1
threshold

"""### Inisiasi Fungsi Callback"""

# Inisiasi fungsi callback dengan syarat akurasi 90%
class myCallback(tf.keras.callbacks.Callback):
  def on_epoch_end(self, epoch, logs={}):
    if (logs.get('mae')<threshold) & (logs.get('val_mae')<threshold):
      print('\nMAE telah mencapai <10%!')
      self.model.stop_training = True

# Inisiasi class myCallback ke dalam variable callbacks
callbacks = myCallback()

"""## Compile dan Training Model"""

# Compile Model
optimizer = tf.keras.optimizers.SGD(learning_rate=1.0000e-04, momentum=0.9)
model.compile(
    loss=tf.keras.losses.Huber(),
    optimizer=optimizer,
    metrics=["mae"])

# Training Model
history = model.fit(
    train_set,                  # Data Train
    epochs=100,                 # Jumlah Epoch
    validation_data=test_set,   # Data Test
    callbacks=callbacks,        # Memanggil Fungsi Callback
    verbose=1)                  # Menampilkan Hasil Tiap Epoch

import matplotlib.pyplot as plt

# Ekstrak MAE dan loss dari training model
mae = history.history['mae']
val_mae = history.history['val_mae']
loss = history.history['loss']
val_loss = history.history['val_loss']

epochs = range(1, len(mae) + 1)

# Plot MAE training dan validasi
plt.plot(epochs, mae, 'bo', label='Training MAE')
plt.plot(epochs, val_mae, 'b', label='Validation MAE')
plt.title('Training and validation MAE')
plt.legend()

# Plot loss training dan validasi
plt.figure()
plt.plot(epochs, loss, 'bo', label='Training loss')
plt.plot(epochs, val_loss, 'b', label='Validation loss')
plt.title('Training and validation loss')
plt.legend()

plt.show()