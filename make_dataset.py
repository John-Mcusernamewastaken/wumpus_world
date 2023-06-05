import numpy as np
import os.path
from wumpus_worldgen import generate_random_world

FILE_PATH = "10k_wumpus_worlds.npy"
DATASET_SIZE = 10000

if os.path.isfile(FILE_PATH):
    worlds = set(np.load(FILE_PATH, allow_pickle=True))
    print(len(worlds))
    for world in worlds:
        print(world.toString())
else:
    worlds = set()
    for i in range(0,DATASET_SIZE):
        print(f"{i}/{DATASET_SIZE}")
        world = generate_random_world(i)
        #print(world.toString())
        worlds.add(world)
    np.save(FILE_PATH, list(worlds), allow_pickle=True)