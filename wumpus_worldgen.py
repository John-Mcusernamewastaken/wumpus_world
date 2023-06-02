from wumpus_world import Action, AgentAvatar, Facing, Percept, Position, World
from wumpus_agent import LuckySearchAgent
import random
from copy import copy

def generate_random_world(nPits):
    def _generate_random_world(nPits:int, dFeasible:list[tuple[int,int]], gFeasible:list[tuple[int,int]], world:World=None) -> World | None: #adds missing features to world
        def placeA(world:World, thing:Percept, coords:tuple[int,int]) -> World | None: #attempt to place a thing in world. Returns a new world with the thing placed, or None if the placement produced an unsolvable world.
            def manhattanDistance(c1, c2):
                x1,y1 = c1
                x2,y2 = c2
                return abs(x1-x2) + abs(y1-y2)
            def solvable(world:World) -> bool:
                worldCopy = world.deepcopy()
                agent = LuckySearchAgent(None, 25, random.choice(list(worldCopy.percepts[Percept.GLITTER])), worldCopy.agentAvatar.position.deepcopy())
                percept = worldCopy.perceived_by_agent()
                while Percept.GLITTER not in percept:
                    if Percept.WUMPUS in percept or Percept.PIT in percept: #TODO remove
                        raise RuntimeError
                    match agent.act(percept):  #prompt the agent. update the agent, world, and percept according to its action
                        case Action.MOVE:
                            worldCopy.move()
                        case Action.TURN_LEFT:
                            worldCopy.turn_left()
                        case Action.TURN_RIGHT:
                            worldCopy.turn_right()
                        case Action.SHOOT:
                            worldCopy.shoot()
                        case Action.PASS:
                            return False
                        case None:
                            raise RuntimeError
                    percept = worldCopy.perceived_by_agent() #update percept
                return True
            def hSolvable(world:World) -> bool|None: #returns the solvability of the world, or None if nothing can be inferred about world's solvability
                def sectorsSolvable(world:World, start:tuple[int,int]) -> bool:
                    def sectorOf(position:tuple[int,int]) -> int:
                        match position:
                            case (0,0) | (1,0) | (0,1) | (1,1):
                                return 0
                            case (2,0) | (3,0) | (2,1) | (3,1):
                                return 1
                            case (0,2) | (1,2) | (0,3) | (1,3):
                                return 2
                            case (2,2) | (3,2) | (2,4) | (3,4):
                                return 3
                    def sectors(world:World) -> tuple[bool,bool,bool,bool]:
                        def pitDanger(world:World, room:tuple[int,int]) -> bool:
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
                            pitDanger(world, (0,0)) and pitDanger(world, (1,0)) and pitDanger(world, (0,1)) and pitDanger(world, (1,1)),
                            pitDanger(world, (2,0)) and pitDanger(world, (3,0)) and pitDanger(world, (2,1)) and pitDanger(world, (3,1)),
                            pitDanger(world, (0,2)) and pitDanger(world, (1,2)) and pitDanger(world, (0,3)) and pitDanger(world, (1,3)),
                            pitDanger(world, (2,2)) and pitDanger(world, (3,2)) and pitDanger(world, (2,4)) and pitDanger(world, (3,4)) 
                        )
                    a,b,c,d = sectors(world)
                    for end in world.percepts[Percept.GLITTER]:
                        match sectorOf(start), sectorOf(end):
                            case (0,1) | (1,0):
                                if a and b:
                                    return True
                            case (0,2) | (2,0):
                                if a and c:
                                    return True
                            case (0,3) | (3,0):
                                if a and d and (b or c):
                                    return True
                            case (1,2) | (2,1):
                                if b and c and (a or d):
                                    return True
                            case (1,3) | (3,1):
                                if b and d:
                                    return True
                            case (2,3) | (3,2):
                                if c and d:
                                    return True
                            case _:
                                return True #both in same quadrant
                    return False
                def trivialPath(world:World) -> bool: #returns true if there is a trivial (0 or 1 turn) path to the treasure 
                    return False
                if manhattanDistance(world.agentAvatar.position.coords, random.choice(list(world.percepts[Percept.GLITTER]))) == 1:
                    return True
                if trivialPath(world):
                    return True
                elif not sectorsSolvable(world, world.agentAvatar.position.coords):
                    return False
                else:
                    return None
            succ = world.deepcopy()
            succ.percepts[thing].add(copy(coords))
            match thing:
                case Percept.WUMPUS:
                    succ.update_adjacent(Percept.WUMPUS, Percept.STENCH)
                case Percept.PIT:
                    succ.update_adjacent(Percept.PIT, Percept.BREEZE)
            match hSolvable(succ):
                case True:
                    return succ
                case None:
                    if solvable(succ):
                        return succ
                    else:
                        return None
                case False:
                    return None
        #depth-first search
        #for each successor (must be iterated in a random order)
        #first, attempt to prove it is unsolvable via heuristic methods
            #sectoring
            #generate a confidence score and discard below a threshold?
        #second, attempt to prove it is unsolvable using a search agent (brute-force every possibility)
        #if a safe placement is found, continue generating
            #otherwise generation failed further down the line, try the next successor
        #if we exhaust all successors without successfully generating a world, backtrack
        #order of operations
        if world is None:
            return None
        else:
            if len(world.percepts[Percept.GLITTER])<1: #place treasure until we have 1
                for coords in dFeasible:
                    dFeasible.remove(coords)
                    gFeasible.remove(coords)
                    succ = _generate_random_world(nPits, dFeasible.copy(), gFeasible.copy(), placeA(world, Percept.GLITTER, coords))
                    if succ is not None: #iff generation succeeded, halt
                        return succ 
                return None #generation has failed
            elif len(world.percepts[Percept.WUMPUS])<1: #place wumpus until we have 1
                for coords in dFeasible:
                    dFeasible.remove(coords)
                    gFeasible.remove(coords)
                    succ = _generate_random_world(nPits, dFeasible.copy(), gFeasible.copy(), placeA(world, Percept.WUMPUS, coords))
                    if succ is not None: #iff generation succeeded, halt
                        return succ
                return None #generation has failed
            elif len(world.percepts[Percept.PIT])<nPits: #place pits until we have nPits
                for coords in dFeasible: #try every coordinate
                    dFeasible.remove(coords)
                    gFeasible.remove(coords)
                    succ = _generate_random_world(nPits, dFeasible.copy(), gFeasible.copy(), placeA(world, Percept.PIT, coords))
                    if succ is not None: #iff generation succeeded, halt
                        return succ
                return None #generation has failed
            else:
                return world #generation is finished
    if nPits>12:
        return None #no solvable world has more than 12 pits
    else:
        #place the agent first, this allows us to remove some rooms from the feasible region
        exitPosition = (random.randint(0,3), random.randint(0,3))
        world = World(
            AgentAvatar(Position(exitPosition, random.choice(list(Facing))), 0, 1),
            exitPosition,
            {
                Percept.BREEZE:  set(),
                Percept.GLITTER: set(),
                Percept.PIT:     set(),
                Percept.STENCH:  set(),
                Percept.WUMPUS:  set()
            }
        )
        #init feasible region
        dFeasible = set()
        for i in range(0,4):
            for j in range(0,4):
                dFeasible.add((i,j))
        dFeasible.remove(world.agentAvatar.position.coords) #nothing else can be in the agent's start room
        gFeasible = dFeasible.copy()
        #dangers cannot be cardinally adjacent to the agent's start room
        dFeasible.discard((world.agentAvatar.position.coords[0]-1, world.agentAvatar.position.coords[1]))
        dFeasible.discard((world.agentAvatar.position.coords[0]+1, world.agentAvatar.position.coords[1]))
        dFeasible.discard((world.agentAvatar.position.coords[0], world.agentAvatar.position.coords[1]-1))
        dFeasible.discard((world.agentAvatar.position.coords[0], world.agentAvatar.position.coords[1]+1))
        #iff the agent is in a corner, dangers cannot be in the diagonally adjacent room
        if world.agentAvatar.position.coords==(0,0): #topleft
            dFeasible.discard((1,1))
        elif world.agentAvatar.position.coords==(3,0): #top-right
            dFeasible.discard((1,2))
        elif world.agentAvatar.position.coords==(0,3): #bottom-left
            dFeasible.discard((2,1))
        elif world.agentAvatar.position.coords==(3,3): #bottom-right
            dFeasible.discard((2,2))
        dFeasible = list(dFeasible)
        gFeasible = list(gFeasible)
        random.shuffle(dFeasible)
        random.shuffle(gFeasible)
        return _generate_random_world(nPits, dFeasible, gFeasible, world)