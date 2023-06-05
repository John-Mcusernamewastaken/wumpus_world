from wumpus_world import Action, Agent, AgentAvatar, Facing, Percept, Position, World
from wumpus_search_agents import SearchAgent, LuckySearchAgent
from wumpus_worldgen import generate_random_world
import random
import time

def print_world(world):
        for j in range(0,4):
            for i in range(0,4):
                print("[", end="")
                if world.agentAvatar.position.coords==(i,j):
                    match world.agentAvatar.position.facing:
                        case Facing.UP:
                            print("↑", end="")
                        case Facing.DOWN:
                            print("↓", end="")
                        case Facing.LEFT:
                            print("←", end="")
                        case Facing.RIGHT:
                            print("→", end="")
                else:
                    print ("_", end="")
                room = list(world.perceived_at(Position((i,j), None)))
                if Percept.WUMPUS in room:
                    print("W", end="")
                else:
                    print ("_", end="")
                if Percept.STENCH in room:
                    print("S", end="")
                else:
                    print ("_", end="")
                if Percept.PIT in room:
                    print("P", end="")
                else:
                    print ("_", end="")
                if Percept.BREEZE in room:
                    print("B", end="")
                else:
                    print ("_", end="")
                if Percept.GLITTER in room:
                    print("G", end="")
                else:
                    print ("_", end="")
                print("]", end="")
            print("\n")
        print("\n")
def test_agent(agent:Agent, world:World, printOut:bool=True, godMode:bool=False, turnLimit:None|int=None) -> None:
    percept = world.perceived_by_agent()
    while turnLimit is None or turnLimit>0:
        action = agent.act(percept) #prompt the agent
        if printOut:
            print("The agent decided to ", end="")
        percept = set()
        match action:  #update the agent, world, and percept according to the action
            case Action.MOVE:
                if printOut:
                    print("move", end="")
                agent.modify_score(-1) #for moving
                if not world.move(): #if the agent bumped
                    percept.add(Percept.BUMP)
                    if printOut:
                        print(", and bumped into a wall.")
                else:
                    if printOut:
                        print(".")
            case Action.TURN_LEFT:
                world.turn_left()
                if printOut:
                    print("turn left.")
            case Action.TURN_RIGHT:
                world.turn_right()
                if printOut:
                    print("turn right.")
            case Action.SHOOT:
                agent.modify_score(-10) #for using an arrow
                if world.shoot():
                    percept.add(Percept.SCREAM) #if a wumpus was killed, it screams, add to percept
                    if printOut:
                        print("shoot, and killed the wumpus!")
                else:
                    if printOut:
                        print("shoot, but missed...")
            case Action.DIG:
                if world.dig(): #if treasure was found
                    if printOut:
                        print("dig, and found treasure!")
                else:
                    if printOut:
                        print("dig, but found nothing...")
            case Action.PASS:
                if printOut:
                    print("do nothing.")
                raise RuntimeError
            case _:
                raise RuntimeError
        percept.update(world.perceived_by_agent()) #add all percepts from current room
        if (Percept.WUMPUS in percept):
            if printOut:
                print("\nAnd was eaten by the wumpus...")
            agent.modify_score(-1000) #for dying
            if printOut and godMode:
                print_world(world)
            break
        elif(Percept.PIT in percept):
            if printOut:
                print("\nAnd fell into a pit...")
            agent.modify_score(-1000) #for dying
            if printOut and godMode:
                print_world(world)
            break
        else:
            if world.agentAvatar.position.coords==world.exitCoords and world.agentAvatar.treasure>0:
                if printOut:
                    print("\nAnd escaped with the treasure!")
                agent.modify_score(world.agentAvatar.treasure*1000) #+1000 for each piece of treasure collected
                if printOut and godMode:
                    print_world(world)
                break #and end the game
            else:
                if printOut and godMode:
                    print_world(world)
        if turnLimit is not None:
            turnLimit = turnLimit-1 #decrement t
        #sleep(.5)
    if turnLimit is not None and turnLimit==0:
        print("\nAgent starved...")
        agent.modify_score(-1000) #for dying

CANONICAL_WORLDS = [
    World(
        agentAvatar=AgentAvatar(Position((0,3), Facing.UP), treasure=0, arrows=1),
        exitCoords=(0,3),
        percepts={
            Percept.WUMPUS:  set([(2,1)]), #the wumpus must be shot to solve this world 
            Percept.STENCH:  set(),
            Percept.PIT:     set([(0,1), (3,0)]),
            Percept.BREEZE:  set(),
            Percept.GLITTER: set([(2,0)])
        }
    )
    ,World(
        agentAvatar=AgentAvatar(Position((0,3), Facing.UP), treasure=0, arrows=1),
        exitCoords=(0,3),
        percepts={
            Percept.WUMPUS:  set([(0,1)]),
            Percept.STENCH:  set(),
            Percept.PIT:     set([(3,0), (2,1), (2,3)]),
            Percept.BREEZE:  set(),
            Percept.GLITTER: set([(1,1)])
        }
    )
    ,World(
        agentAvatar=AgentAvatar(Position((2,1), Facing.UP), treasure=0, arrows=1),
        exitCoords=(2,1),
        percepts={
            Percept.WUMPUS:  set([(1,0)]),
            Percept.STENCH:  set(),
            Percept.PIT:     set([(0,1), (0,3), (1,3)]),
            Percept.BREEZE:  set(),
            Percept.GLITTER: set([(1,2)])
        }
    )
    ]
for world in CANONICAL_WORLDS:
    world.update_adjacent(Percept.WUMPUS, Percept.STENCH)
    world.update_adjacent(Percept.PIT, Percept.BREEZE)

TEST_AGENTS = True
TEST_WORLDGEN = False
ITERATIONS = 1

match TEST_AGENTS, TEST_WORLDGEN:
    case False, False:
        pass
    case False, True:
        for _ in range(0, ITERATIONS):
            randomWorld = generate_random_world(3)
            if randomWorld is None:
                raise RuntimeError
            else:
                print_world(randomWorld)
    case True, False:
        for world in CANONICAL_WORLDS: #TODO multithread
            AGENTS = [
                SearchAgent(
                    "     SearchAgent",
                    10,
                    world.agentAvatar.position.deepcopy()
                ),
                LuckySearchAgent(
                    "LuckySearchAgent",
                    10,
                    random.choice(list(world.percepts[Percept.GLITTER])),
                    world.agentAvatar.position.deepcopy()
                )
            ]
            for agent in AGENTS:
                start = time.perf_counter()
                test_agent(
                    agent,
                    world.deepcopy(),
                    printOut=True,
                    godMode=True
                )
                end = time.perf_counter()
                agent.time = (end-start)
            for agent in AGENTS:
                print(agent.toString(), f"In {agent.time:0.6f}s.")
    case True, True:
        for _ in range(0, ITERATIONS):
            randomWorld = generate_random_world(random.randint(0,6))
            if randomWorld is None:
                raise RuntimeError
            else:
                AGENTS = [
                    SearchAgent(
                        "     SearchAgent",
                        25,
                        #random.choice(list(realWorld.percepts[Percept.GLITTER])),
                        randomWorld.agentAvatar.position.deepcopy()
                    ),
                    LuckySearchAgent(
                        "LuckySearchAgent",
                        25,
                        random.choice(list(randomWorld.percepts[Percept.GLITTER])),
                        randomWorld.agentAvatar.position.deepcopy()
                    )
                ]
                for agent in AGENTS:
                    start = time.perf_counter()
                    test_agent(
                        agent,
                        randomWorld.deepcopy(),
                        printOut=True,
                        godMode=True,
                        turnLimit=25
                    )
                    end = time.perf_counter()
                    agent.time = (end-start)
                    #sleep(2.5)
                for agent in AGENTS:
                    print(agent.toString(), f"In {agent.time:0.6f}s.")