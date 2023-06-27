import numpy as np
from tensorflow.python.keras.models import Sequential
from tensorflow.python.keras.layers import Dense

TRAIN_FILE = "wwlearn_train_100k.npy"
TEST_FILE = "wwlearn_test_10k.npy"

train = np.load(TRAIN_FILE)
test = np.load(TEST_FILE)

model = Sequential()