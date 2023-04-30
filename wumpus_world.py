from __future__ import annotations
from enum import Enum

class Action(Enum):
    MOVE       = 1
    TURN_LEFT  = 2
    TURN_RIGHT = 3
    SHOOT      = 4
    DIG        = 5
class Facing(Enum):
    UP    = 1
    DOWN  = 2
    LEFT  = 3
    RIGHT = 4
class Percept(Enum):
    WUMPUS  = 0
    STENCH  = 1
    PIT     = 2
    BREEZE  = 3
    GLITTER = 4
    BUMP    = 5
    SCREAM  = 6

class Position():
    def __init__(self, coords, facing):
        self.coords = coords
        self.facing = facing
    
    def ahead(self) -> Position | None:
        oldX, oldY = self.coords
        newX = -1
        newY = -1
        match self.facing: #get coords after move
            case Facing.UP:
                newX = oldX
                newY = oldY-1
            case Facing.DOWN:
                newX = oldX
                newY = oldY+1
            case Facing.LEFT:
                newX = oldX-1
                newY = oldY
            case Facing.RIGHT:
                newX = oldX+1
                newY = oldY
        if newX>=0 and newX<=3 and newY>=0 and newY <=3:
            return Position((newX, newY), self.facing)
        else:
            return None
    def left(self) -> Position:
        match self.facing:
            case Facing.UP:
                return Position(self.coords, Facing.LEFT)
            case Facing.DOWN:
                return Position(self.coords, Facing.RIGHT)
            case Facing.LEFT:
                return Position(self.coords, Facing.DOWN)
            case Facing.RIGHT:
                return Position(self.coords, Facing.UP)
    def right(self) -> Position:
        match self.facing:
            case Facing.UP:
                return Position(self.coords, Facing.RIGHT)
            case Facing.DOWN:
                return Position(self.coords, Facing.LEFT)
            case Facing.LEFT:
                return Position(self.coords, Facing.UP)
            case Facing.RIGHT:
                return Position(self.coords, Facing.DOWN)

class Agent:
    def __init__(self) -> None:
        self.score = 0
    def modify_score(self, change) -> None:
        self.score = self.score + change
    def act(self, _:list(Percept)) -> Action: #return an action based on a set of percepts
        pass
class InputAgent(Agent):
    def act(self, percept:set(Percept)) -> Action:
        percept = list(percept)
        if percept==[]:
            print("This room is empty.\n")
        else:
            print("You ", end="")
            while percept!=[]:
                next = percept.pop()
                match next:
                    case Percept.STENCH:
                        print("smell a stench", end="")
                    case Percept.BREEZE:
                        print("feel a breeze", end="")
                    case Percept.GLITTER:
                        print("see glittering dust on the floor", end="")
                if len(percept)>1:
                    print(", ", end="")
                elif len(percept)==1:
                    print(", and ", end="")
            print(".\n")
        while True:
            res = input("Enter an action:")
            match res:
                case "move" | "m":
                    return Action.MOVE
                case "left" | "l":
                    return Action.TURN_LEFT
                case "right" | "r":
                    return Action.TURN_RIGHT
                case "shoot" | "s":
                    return Action.SHOOT
                case "dig" | "d":
                    return Action.DIG
                case "help":
                    print("move - move forward\nleft - turn left\nright - turn right\nshoot - shoot your arrow\ndig - dig for treasure")
                case _:
                    print("invalid action")
class PlanningAgent(Agent):
    def __init__(self):
        self.world = {
            Percept.WUMPUS:  set(),
            Percept.STENCH:  set(),
            Percept.PIT:     set(),
            Percept.BREEZE:  set(),
            Percept.GLITTER: set()
        }
    def next_states(self):
        return [
            #move
            #left
            #right
            #shoot
            #dig
        ]
    def act(self, _:set(Percept)) -> Action:
        #add current percept to world model
        #attempt to deduce features of world based on model
        #generate next states (?)
        raise NotImplementedError

class World():
    class AgentAvatar:
        def __init__(self, position, treasure, arrows) -> None:
            self.position = position
            self.treasure = treasure
            self.arrows = arrows
        def turn_left(self) -> None:
            self.position = Position.left(self.position)
        def turn_right(self) -> None:
            self.position = Position.right(self.position)
        def move(self) -> bool: #updates the coords to move the agent, returns true if the position was changed, false otherwise
            newPosition = self.position.ahead()
            if newPosition == None:
                return False
            else:
                self.position = newPosition
                return True
        def shoot(self) -> None:
            if self.arrows>0:
                self.arrows = self.arrows-1
            else:
                raise RuntimeError #don't do this
        def add_treasure(self, n:int) -> None:
            self.treasure = self.treasure+n
    def __init__(self) -> None:
        self.agentAvatar = self.AgentAvatar(Position((0,3), Facing.RIGHT), treasure=0, arrows=1)
        self.percepts = {
            Percept.WUMPUS:  set([(0,1)]),
            Percept.STENCH:  set(),
            Percept.PIT:     set([(3,0), (2,1), (2,3)]),
            Percept.BREEZE:  set(),
            Percept.GLITTER: set([(1,1)])
        }
        self.update_adjacent(Percept.WUMPUS, Percept.STENCH)
        self.update_adjacent(Percept.PIT, Percept.BREEZE)
    def update_adjacent(self, source:Percept, signal:Percept) -> None: #updates the world, adding a signal to all rooms adjacent to a source
        self.percepts[signal] = set() #remove all existing signals
        for wumpus in self.percepts[source]: #for every source
            for facing in list(Facing): #for every room adjacent to that source
                target = Position(wumpus, facing).ahead()
                if target!=None:
                    self.percepts[signal].add(target.coords) #add a signal
    def move(self) -> None:
        return self.agentAvatar.move()
    def turn_left(self) -> None:
        return self.agentAvatar.turn_left()
    def turn_right(self) -> None:
        return self.agentAvatar.turn_right()
    def perceived_at(self, position:Position) -> set(Percept):
        perceivedHere = set()
        for (kind, coordss) in self.percepts.items(): #add all 
            if position.coords in coordss:
                perceivedHere.add(kind)
        return perceivedHere
    def perceived_by_agent(self) -> set(Percept): #returns all percepts perceived at coords
        return self.perceived_at(self.agentAvatar.position)
    def shoot(self) -> bool:#returns true if a wumpus was killed, false otherwise
        self.agentAvatar.shoot()
        target = world.agentAvatar.position.ahead()
        if target in self.percepts[Percept.WUMPUS]: #if we hit a wupus
            self.percepts[Percept.WUMPUS].remove(target) #remove the wumpus
            self.update_adjacent(Percept.WUMPUS, Percept.STENCH) #wumpus changed, so update stench 
            return True #we killed a wumpus
        else:
            return False #we didn't kill a wumpus
    def dig(self) -> bool: #returns true if treasure was found
        if world.agentAvatar.position.coords in self.percepts[Percept.GLITTER]:
            self.percepts[Percept.GLITTER].remove(world.agentAvatar.position.coords) #remove the treasure
            self.agentAvatar.add_treasure(1) #add to agent
            return True
        else:
            return False

def print_world(world):
    for j in range(0,4):
        for i in range(0,4):
            print("[", end="")
            room = list(world.perceived_at(Position((i,j), None)))
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
                if(room!=[]):
                    print(", ", end="")
            while room!=[]:
                next = room.pop()
                match next:
                    case Percept.WUMPUS:
                        print("🐉", end="")
                    case Percept.STENCH:
                        print("👃", end="")
                    case Percept.PIT:
                        print("●", end="")
                    case Percept.BREEZE:
                        print("〰", end="")
                    case Percept.GLITTER:
                        print("💰", end="")
                if room!=[]:
                    print(", ", end="")
            print("]", end="")
        print("\n")
    print("\n")

agent = InputAgent()
world = World()
percept = world.perceived_by_agent()
GOD_MODE = False
if(GOD_MODE):
    print_world(world)    
while(True):
    action = agent.act(percept) #prompt the agent
    print("The agent decided to ", end="")
    percept = set()
    match action:  #update the agent, world, and percept according to the action
        case Action.MOVE:
            print("move", end="")
            agent.modify_score(-1) #for moving
            if not world.move(): #if the agent bumped
                percept.add(Percept.BUMP)
                print(", and bumped into a wall.")
            else:
                print(".")
        case Action.TURN_LEFT:
            world.turn_left()
            print("turn left.")
        case Action.TURN_RIGHT:
            world.turn_right()
            print("turn right.")
        case Action.SHOOT:
            agent.modify_score(-10) #for using an arrow
            if world.shoot():
                percept.add(Percept.SCREAM) #if a wumpus was killed, it screams, add to percept
                print("shoot, and killed the wumpus!")
            else:
                print("shoot, but missed...")
        case Action.DIG:
            if world.dig(): #if treasure was found
                print("dig, and found treasure!")
            else:
                print("dig, but found nothing...")
    percept.update(world.perceived_by_agent()) #add all percepts from current room
    if (Percept.WUMPUS in percept):
        print("\nAnd was eaten by the wumpus...")
        agent.modify_score(-1000) #for dying
        if GOD_MODE:
            print_world(world)
        break
    elif(Percept.PIT in percept):
        print("\nAnd fell into a pit...")
        agent.modify_score(-1000) #for dying
        if GOD_MODE:
            print_world(world)
        break
    else:
        if world.agentAvatar.position.coords==(0,3) and world.agentAvatar.treasure>0:
            print("\nAnd escaped with the treasure!")
            agent.modify_score(world.agentAvatar.treasure*1000) #+1000 for each piece of treasure collected
            if GOD_MODE:
                print_world(world)
            break #and end the game
        else:
            if(GOD_MODE):
                print_world(world)    
print("Score:", agent.score)