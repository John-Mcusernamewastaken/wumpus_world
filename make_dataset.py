import numpy as np
import os.path
from wumpus_worldgen import generate_random_world
from wumpus_world import World

FILE_PATH = "100k_wumpus_worlds.npy"
DATASET_SIZE = 100000

if os.path.isfile(FILE_PATH):
    print(len(set(np.load(FILE_PATH, allow_pickle=True))))
else:
    worlds = set()
    for i in range(543,DATASET_SIZE):
        print(f"{i}/{DATASET_SIZE}")
        world = generate_random_world(i)
        #print(world.toString())
        worlds.add(world)
    np.save(FILE_PATH, list(worlds), allow_pickle=True)