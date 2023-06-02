from __future__ import annotations
from wumpus_world import Action, Agent, AgentAvatar, Facing, Percept, Position, World

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
                    case Percept.BUMP:
                        print("feel yourself bump into a wall", end="")
                    case Percept.SCREAM:
                        print("hear an unearthly scream", end="")
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
class SearchAgent(Agent):
    def __init__(self, name, searchDepth, startPosition=Position((0,3), Facing.UP)):
        super().__init__(name)
        self.prevAction = None
        self.searchDepth = searchDepth
        self.innerWorld = World(
            AgentAvatar(startPosition, treasure=0, arrows=1),
            startPosition.coords,
            {
                Percept.WUMPUS:  set(),
                Percept.STENCH:  set(),
                Percept.PIT:     set(),
                Percept.BREEZE:  set(),
                Percept.GLITTER: set()
            }
        )
        self.safe = set()
        self.explored = set()
        self.agendaKey = (lambda x: x[2]) #depth
    def act(self, percepts:set(Percept)) -> Action:
        def search(self, isGoal:function, maxDepth:int) -> Action: #attempt to reach a room that fulfills a predicate isGoal, while only visiting safe rooms
            def next_states(state) -> list(Position):
                _, position, len, visited, sinceMove = state
                if len>maxDepth: #depth cutoff
                    return []
                elif sinceMove==3: #kill spinners, turning >3 times is never rational (just turn the other way)
                    return []
                else:
                    states = [(Action.TURN_LEFT, position.left(), len+1, visited, sinceMove+1), (Action.TURN_RIGHT, position.right(), len+1, visited, sinceMove+1)]
                    ahead = position.ahead()
                    if ahead!=None:
                        x,y = ahead.coords
                        if ((x,y) not in visited) and ((x,y) in self.safe): #paths cannot cycle or explore unsafe tiles
                            newVisited = visited + ((x,y),)
                            states.append((Action.MOVE, ahead, len+1, newVisited, 0))
                    return states
            def backtrack(state):
                head = state
                while prev[head] in prev: #intentional, stop at the second-to-last action
                    head = prev[head]
                return head
            agenda = [(None, self.innerWorld.agentAvatar.position, 1, (), 0)] #previous action, position, depth, rooms visited, turns since move
            dist = dict()
            prev = dict()
            while not agenda==[]:
                agenda.sort(key=self.agendaKey) #uniform cost search
                head = agenda.pop(0)
                keyH = (head[0],head[1])
                x,y = head[1].coords
                if isGoal(x,y):
                    return backtrack(keyH)[0]
                for state in next_states(head):
                    keyS = (state[0],state[1])
                    if state not in agenda and ((keyS not in dist) or (dist[keyS]>state[2])): #if this is new best
                        agenda.append(state)
                        dist[keyS] = state[2]
                        prev[keyS] = keyH
            return None
        #update mental position according to real movement
        if self.prevAction==Action.TURN_LEFT:
            self.innerWorld.agentAvatar.turn_left()
        elif self.prevAction==Action.TURN_RIGHT:
            self.innerWorld.agentAvatar.turn_right()
        elif (self.prevAction==Action.MOVE) and (Percept.BUMP not in percepts):
            self.innerWorld.agentAvatar.move()
        
        if self.innerWorld.agentAvatar.treasure>0: #we have the treasure, so return to exit
            self.prevAction = search(self, 
                isGoal=(lambda x,y: x==self.innerWorld.exitCoords[0] and y==self.innerWorld.exitCoords[1]),
                maxDepth=self.searchDepth
            )
            return self.prevAction
        else: #search for treasure
            self.explored.add(self.innerWorld.agentAvatar.position.coords)
            self.safe.add(self.innerWorld.agentAvatar.position.coords)
            if Percept.GLITTER in percepts: #dig treasure if possible
                self.prevAction = Action.DIG
                self.innerWorld.agentAvatar.add_treasure(1)
                return self.prevAction
            else:
                #update model with percepts
                for percept in percepts:
                    if (percept==Percept.STENCH) or (percept==Percept.BREEZE): #danger sources
                        self.innerWorld.percepts[percept].add(self.innerWorld.agentAvatar.position.coords)
                #deduce safe tiles
                for y in range(0,4):
                    for x in range(0,4):
                        if (
                        (
                            ((x-1,y) in self.explored and (x-1,y) not in self.innerWorld.percepts[Percept.STENCH]) or #adjacent without stench (no wumpus)
                            ((x+1,y) in self.explored and (x+1,y) not in self.innerWorld.percepts[Percept.STENCH]) or
                            ((x,y-1) in self.explored and (x,y-1) not in self.innerWorld.percepts[Percept.STENCH]) or
                            ((x,y+1) in self.explored and (x,y+1) not in self.innerWorld.percepts[Percept.STENCH])
                        ) and
                        (
                            ((x-1,y) in self.explored and (x-1,y) not in self.innerWorld.percepts[Percept.BREEZE]) or #adjacent without breeze (no pit)
                            ((x+1,y) in self.explored and (x+1,y) not in self.innerWorld.percepts[Percept.BREEZE]) or
                            ((x,y-1) in self.explored and (x,y-1) not in self.innerWorld.percepts[Percept.BREEZE]) or
                            ((x,y+1) in self.explored and (x,y+1) not in self.innerWorld.percepts[Percept.BREEZE])
                        )):
                            self.safe.add((x,y))
                action = search(self, 
                    isGoal=(lambda x,y: (x,y) not in self.explored),
                    maxDepth=self.searchDepth
                )
                if action is not None:  
                    self.prevAction = action
                    return self.prevAction
                else:
                    #try to hunt the wumpus
                    def in_shooting_position(x,y):
                        return (( #below the wumpus and facing up
                            self.innerWorld.agentAvatar.position.facing==Facing.UP and
                            self.innerWorld.agentAvatar.position.coords[0]==x and
                            self.innerWorld.agentAvatar.position.coords[0]==y+1
                        ) or
                        ( #above the wumpus and facing down
                            self.innerWorld.agentAvatar.position.facing==Facing.DOWN and
                            self.innerWorld.agentAvatar.position.coords[0]==x and
                            self.innerWorld.agentAvatar.position.coords[0]==y-1
                        ) or
                        ( #right of the wumpus and facing left
                            self.innerWorld.agentAvatar.position.facing==Facing.LEFT and
                            self.innerWorld.agentAvatar.position.coords[0]==x+1 and
                            self.innerWorld.agentAvatar.position.coords[0]==y
                        ) or
                        ( #left of the wumpus and facing right
                            self.innerWorld.agentAvatar.position.facing==Facing.RIGHT and
                            self.innerWorld.agentAvatar.position.coords[0]==x-1 and
                            self.innerWorld.agentAvatar.position.coords[0]==y
                        ))
                    if in_shooting_position(self.innerWorld.agentAvatar.position.coords[0],self.innerWorld.agentAvatar.position.coords[1]): #shoot if in position
                        return Action.SHOOT
                    else: #move to shooting position
                        action = search(self, 
                            isGoal=in_shooting_position,
                            maxDepth=self.searchDepth
                        )
                        if action is not None:
                            self.prevAction = action
                            return self.prevAction
                        else:
                            return Action.PASS #unsolvable, give up
class LuckySearchAgent(SearchAgent): #uses manhattan distance from treasure to "lucky guess" paths
    def __init__(self, name, searchDepth, treasureCoords:tuple(int,int), exitPosition=Position((0, 3), Facing.UP)):
        super().__init__(name, searchDepth, exitPosition)
        self.agendaKey = (lambda x: abs(x[1].coords[0]-treasureCoords[0]) + abs(x[1].coords[1]-treasureCoords[1])) #manhattan distance to treasure
