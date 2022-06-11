import tensorflow_decision_forests as tfdf

import os
import numpy as np
import pandas as pd
import tensorflow as tf
import math

from fmexp.fmclassify import FMClassifier


# Check the version of TensorFlow Decision Forests
print("Found TensorFlow Decision Forests v" + tfdf.__version__)
# Split the dataset into a training and a testing dataset.

def split_dataset(dataset, test_ratio=0.30):
  """Splits a panda dataframe in two."""
  test_indices = np.random.rand(len(dataset)) < test_ratio
  return dataset[~test_indices], dataset[test_indices]

fmc = FMClassifier()
fmc.load_data(mode='mouse')

# print('X_train', fmc.X_train)

"""train_ds_pd = pd.DataFrame(data={
  'test': [c[0] for c in fmc.X_train],
})"""

train_ds_pd = pd.DataFrame(data=fmc.X_train)

print('train_ds_pd', train_ds_pd)

"""train_ds_pd, test_ds_pd = split_dataset(dataset_df)
print("{} examples in training, {} examples for testing.".format(
    len(train_ds_pd), len(test_ds_pd)))"""


# train_ds = tfdf.keras.pd_dataframe_to_tf_dataset(train_ds_pd, label='test')
# test_ds = tfdf.keras.pd_dataframe_to_tf_dataset(test_ds_pd, label=label)

# model_1 = tfdf.keras.RandomForestModel()
model_1 = tf.keras.models.Sequential([
  tf.keras.layers.InputLayer(input_shape=(len(fmc.X_train[0]),)),
  tf.keras.layers.Dense(10, kernel_initializer='zeros'),
  tf.keras.layers.Dense(10, kernel_initializer='zeros'),
  tf.keras.layers.Dense(10, kernel_initializer='zeros'),
  tf.keras.layers.Softmax(),
])
model_1.compile(
  optimizer=tf.keras.optimizers.SGD(learning_rate=1.0),
  loss=tf.keras.losses.MeanSquaredError(),
  # loss=tf.keras.losses.SparseCategoricalCrossentropy(),
)

model_1.fit(fmc.X_train, fmc.y_train, epochs=1)
print('evaluate:', model_1.evaluate(fmc.X_test, fmc.y_test, return_dict=True))

model_1.fit(fmc.X_train, fmc.y_train, epochs=20)
print('evaluate:', model_1.evaluate(fmc.X_test, fmc.y_test, return_dict=True))

# print('WEIGHTS:')
# print(model_1.get_weights())
