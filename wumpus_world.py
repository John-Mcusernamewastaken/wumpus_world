from __future__ import annotations
from enum import Enum
from copy import deepcopy

class Action(Enum):
    MOVE       = 1
    TURN_LEFT  = 2
    TURN_RIGHT = 3
    SHOOT      = 4
    DIG        = 5
    PASS       = 6
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
class Agent:
    def __init__(self, name) -> None:
        self.score = 0
        self.name = name
    def modify_score(self, change) -> None:
        self.score = self.score + change
    def act(self, _:list(Percept)) -> Action: #return an action based on a set of percepts
        pass
    def toString(self) -> str:
        return f"{self.name}('score'={self.score})"
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
    def deepcopy(self):
        return Position(deepcopy(self.coords), self.facing)
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
        def deepcopy(self) -> AgentAvatar:
            return AgentAvatar(self.position.deepcopy(), self.treasure, self.arrows)
class World():
    def __init__(self, agentAvatar, exitCoords, percepts) -> None:
        self.agentAvatar = agentAvatar
        self.percepts = percepts
        self.exitCoords = exitCoords
        self.update_adjacent(Percept.WUMPUS, Percept.STENCH)
        self.update_adjacent(Percept.PIT, Percept.BREEZE)
    def update_adjacent(self, source:Percept, signal:Percept) -> None: #updates the world, adding a signal to all rooms adjacent to a source
        self.percepts[signal] = set() #remove all existing signals
        for percept in self.percepts[source]: #for every source
            for facing in list(Facing): #for every room adjacent to that source
                target = Position(percept, facing).ahead()
                if target!=None:
                    self.percepts[signal].add(target.coords) #add a signal
    def move(self) -> bool:
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
        target = self.agentAvatar.position.ahead().coords
        if target in self.percepts[Percept.WUMPUS]: #if we hit a wupus
            self.percepts[Percept.WUMPUS].remove(target) #remove the wumpus
            self.update_adjacent(Percept.WUMPUS, Percept.STENCH) #wumpus changed, so update stench 
            return True #we killed a wumpus
        else:
            return False #we didn't kill a wumpus
    def dig(self) -> bool: #returns true if treasure was found
        if self.agentAvatar.position.coords in self.percepts[Percept.GLITTER]:
            self.percepts[Percept.GLITTER].remove(self.agentAvatar.position.coords) #remove the treasure
            self.agentAvatar.add_treasure(1) #add to agent
            return True
        else:
            return False
    def deepcopy(self) -> World:
        return World(self.agentAvatar.deepcopy(), self.exitCoords, deepcopy(self.percepts))
