from wumpus_world import Action, AgentAvatar, Percept, World
from wumpus_agent import LuckySearchAgent
import random


def generate_random_world(nPits):
    def _generate_random_world(nPits:int, world:World=None) -> World: #adds missing features to world
        def placeA(world:World, thing:Percept) -> World:
            def manhattanDistance(c1, c2):
                x1,y1 = c1
                x2,y2 = c2
                return abs(x1-x2) + abs(y1-y2)
            def solvable(world:World) -> bool:
                agent = LuckySearchAgent(25)
                percept = world.perceived_by_agent()
                while Percept.GLITTER not in percept:
                    if Percept.WUMPUS in percept or Percept.PIT in percept: #TODO remove
                        raise RuntimeError
                    match agent.act(percept):  #prompt the agent. update the agent, world, and percept according to its action
                        case Action.MOVE:
                            world.move()
                        case Action.TURN_LEFT:
                            world.turn_left()
                        case Action.TURN_RIGHT:
                            world.turn_right()
                        case Action.SHOOT:
                            world.shoot()
                        case Action.PASS:
                            return False
                        case None:
                            raise RuntimeError
                    percept = world.perceived_by_agent() #update percept
                return True
            def hSolvable(world:World) -> True | None | False: #returns the solvability of the world, or None if nothing can be inferred about world's solvability
                def sectorsSolvable(world:World, start:int, end:int) -> bool:
                    def sectors(world:World) -> tuple(bool,bool,bool,bool):
                        def pitDanger(world:World, room:tuple(int,int)) -> bool:
                            return (
                                room in world.percepts[Percept.BREEZE] or
                                room in world.percepts[Percept.PIT] or
                                ( #fully surrounded by breeze (indistinguishable from a pit)
                                    (room[0]-1,room[1]) in world.percepts[Percept.BREEZE] and
                                    (room[0]+1,room[1]) in world.percepts[Percept.BREEZE] and
                                    (room[0],room[1]-1) in world.percepts[Percept.BREEZE] and
                                    (room[0],room[1]+1) in world.percepts[Percept.BREEZE]
                                )
                            )
                        return (
                            pitDanger((0,0)) and pitDanger((1,0)) and pitDanger((0,1)) and pitDanger((1,1)),
                            pitDanger((2,0)) and pitDanger((3,0)) and pitDanger((2,1)) and pitDanger((3,1)),
                            pitDanger((0,2)) and pitDanger((1,2)) and pitDanger((0,3)) and pitDanger((1,3)),
                            pitDanger((2,2)) and pitDanger((3,2)) and pitDanger((2,4)) and pitDanger((3,4)) 
                        )
                    a,b,c,d = sectors(world)
                    for treasure in world.percepts[Percept.GLITTER]:
                        match world.exitPosition, treasure:
                            case (a,b) | (b,a):
                                if a and b:
                                    return True
                            case (a,c) | (c,a):
                                if a and c:
                                    return True
                            case (a,d) | (d,a):
                                if a and d and (b or c):
                                    return True
                            case (b,c) | (c,b):
                                if b and c and (a or d):
                                    return True
                            case (b,d) | (d,b):
                                if b and d:
                                    return True
                            case (c,d) | (d,c):
                                if c and d:
                                    return True
                            case _:
                                return True #both in same quadrant
                    return False
                def trivialPath(world:World) -> bool: #returns true if there is a trivial (0 or 1 turn) path to the treasure 
                    raise NotImplementedError
                if manhattanDistance(world.agentAvatar.coords, random.choice(world.percepts[Percept.GLITTER])) == 1:
                    return True
                if trivialPath(world):
                    return True
                elif not sectorsSolvable(world):
                    return False
                else:
                    return None
            raise NotImplementedError
            #depth-first search
            #for each successor (must be iterated in a random order)
            #first, attempt to prove it is unsolvable via heuristic methods
                #sectoring
                #generate a confidence score and discard below a threshold?
            #second, attempt to prove it is unsolvable using a search agent (brute-force every possibility)
            #if a solution is found, continue generating
            if nPits==0:
                return world
            else:
                o = _generate_random_world(nPits-1, world)
                if o is not None: #if we successfully generated a world
                    return o
                #otherwise generation failed further down the line, try the next successor
            #if we exhaust all successors without successfully generating a world, backtrack
        #order of operations
        if world is None: #place agent if none exists
            exitPosition = (random.randint(0,3), random.randint(0,3))
            world = World(AgentAvatar(exitPosition, 0, 1), exitPosition, dict())
            world.percepts[Percept.BREEZE] = set()
            world.percepts[Percept.GLITTER] = set()
            world.percepts[Percept.PIT] = set()
            world.percepts[Percept.STENCH] = set()
            world.percepts[Percept.WUMPUS] = set()
        if len(world.percepts[Percept.GLITTER])<=1: #place treasure until we have 1
            return _generate_random_world(placeA(world, Percept.GLITTER))
        elif len(world.percepts[Percept.WUMPUS])<=1: #place wumpus until we have 1
            return _generate_random_world(placeA(world, Percept.WUMPUS))
        elif len(world.percepts[Percept.PIT])<nPits: #place pits until we have nPits
            return _generate_random_world(placeA(world, Percept.PIT))
    if nPits>12:
        return None #no solvable world has more than 12 pits
    else:
        _generate_random_world(nPits)