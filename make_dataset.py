import numpy as np
import os.path
from wumpus_worldgen import generate_random_world

TRAIN_PATH = "wwlearn_train_100k.npy"
TRAIN_SIZE = 100000
TEST_PATH  = "wwlearn_test_10k.npy"
TEST_SIZE  = 10000

if not os.path.isfile(TRAIN_PATH):
    worlds = set()
    for i in range(0, TRAIN_SIZE+1):
        print(f"{i}/{TRAIN_SIZE}")
        world = generate_random_world(i)
        worlds.add(world)
    np.save(TRAIN_PATH, list(worlds), allow_pickle=True)

if not os.path.isfile(TEST_PATH):
    worlds = set()
    for i in range(TRAIN_SIZE, TRAIN_SIZE+TEST_SIZE+1):
        print(f"{i}/{TRAIN_SIZE+TEST_SIZE}")
        world = generate_random_world(i)
        worlds.add(world)
    np.save(TEST_PATH, list(worlds), allow_pickle=True)