from __future__ import annotations
from wumpus_world import Action, Agent, AgentAvatar, Facing, Percept, Position, World

class InputAgent(Agent):
    def act(self, percept:set[Percept]) -> Action:
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
        self.actionQueue = []
        self.agendaKey = (lambda x: x[2] if self.innerWorld.agentAvatar.treasure==0 else abs(x[1].coords[0]-startPosition.coords[0]) + abs(x[1].coords[1]-startPosition.coords[1])) #search depth, then manhattan distance to exit
    def act(self, percepts:set[Percept]) -> Action:
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
            def backtrack(head):
                actions = []
                while head in prev: #recreate path
                    actions.append(head[0])
                    head = prev[head]
                return actions
            agenda = [(None, self.innerWorld.agentAvatar.position, 1, (), 0)] #previous action, position, depth, visited list, turns since move
            dist = dict()
            prev = dict()
            while not agenda==[]:
                agenda.sort(key=self.agendaKey) #uniform cost search
                head = agenda.pop(0)
                keyH = (head[0],head[1])
                if isGoal(head[1]):
                    return backtrack(keyH)
                else:
                    for state in next_states(head):
                        keyS = (state[0],state[1])
                        if state not in agenda and ((keyS not in dist) or (dist[keyS]>state[2])): #state is not on agenda, and if there is an existing path the new path must be shorter
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
        
        self.explored.add(self.innerWorld.agentAvatar.position.coords)
        self.safe.add(self.innerWorld.agentAvatar.position.coords)
        if self.actionQueue!=[]: #if we have an existing plan, execute it
            self.prevAction = self.actionQueue.pop()
            return self.prevAction
        else: #otherwise make a new plan
            if self.innerWorld.agentAvatar.treasure>0: #we have the treasure, so return to exit
                self.actionQueue.extend(search(self, 
                    isGoal=(lambda position: position.coords==self.innerWorld.exitCoords),
                    maxDepth=self.searchDepth
                ))
                self.prevAction = self.actionQueue.pop()
                return self.prevAction
            else: #search for treasure
                if Percept.GLITTER in percepts: #dig treasure if possible
                    self.prevAction = Action.DIG
                    self.innerWorld.agentAvatar.add_treasure(1)
                    return self.prevAction
                else:
                    #update model with percepts
                    for percept in percepts:
                        if (percept==Percept.STENCH) or (percept==Percept.BREEZE): #danger sources
                            self.innerWorld.percepts[percept].add(self.innerWorld.agentAvatar.position.coords)
                        elif percept==Percept.SCREAM:
                            self.innerWorld.percepts[Percept.STENCH].clear() #wumpus died, clear all stench tiles
                    #deduce wumpus tiles
                    for x in range(0,4):
                        for y in range(0,4):
                            #due to unexplored with adjacent stench
                            u = (x,y-1) in self.innerWorld.percepts[Percept.STENCH]
                            d = (x,y+1) in self.innerWorld.percepts[Percept.STENCH]
                            l = (x-1,y) in self.innerWorld.percepts[Percept.STENCH]
                            r = (x+1,y) in self.innerWorld.percepts[Percept.STENCH]
                            if (u and d and l) or (u and d and r) or (d and l and r) or (u and l and r): #there is a wumpus
                                self.innerWorld.percepts[Percept.WUMPUS].add((x,y))
                            elif (x,y) in self.innerWorld.percepts[Percept.STENCH]:
                                #due to stench with adjacent explored
                                u = (x,y-1) in self.explored
                                d = (x,y+1) in self.explored
                                l = (x-1,y) in self.explored
                                r = (x+1,y) in self.explored
                                if u and d and l:
                                    self.innerWorld.percepts[Percept.WUMPUS].add((x+1,y))
                                elif u and d and r:
                                    self.innerWorld.percepts[Percept.WUMPUS].add((x-1,y))
                                elif d and l and r:
                                    self.innerWorld.percepts[Percept.WUMPUS].add((x,y-1))
                                elif u and l and r:
                                    self.innerWorld.percepts[Percept.WUMPUS].add((x,y+1))
                    #deduce safe tiles
                    for x in range(0,4):
                        for y in range(0,4):
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
                    plan = search(self, 
                        isGoal=(lambda position: position.coords not in self.explored),
                        maxDepth=self.searchDepth
                    )
                    if plan is not None:
                        self.actionQueue.extend(plan)
                        self.prevAction = self.actionQueue.pop()
                        return self.prevAction
                    else:
                        #try to hunt the wumpus
                        def in_shooting_position(position:Position) -> bool:
                            return (position.ahead().coords in self.innerWorld.percepts[Percept.WUMPUS]) #there's a wumpus directly ahead
                        if in_shooting_position(self.innerWorld.agentAvatar.position): #shoot if in position
                            self.prevAction = Action.SHOOT
                            return self.prevAction
                        else: #move to shooting position
                            plan = search(self,
                                isGoal=in_shooting_position,
                                maxDepth=self.searchDepth
                            )
                            if plan is not None: #if we succeeded in creating a movement plan, execute it
                                self.actionQueue.extend(plan)
                                self.prevAction = self.actionQueue.pop()
                                return self.prevAction
                            else:
                                return Action.PASS #unsolvable, give up
class LuckySearchAgent(SearchAgent): #uses manhattan distance from treasure to "lucky guess" paths
    def __init__(self, name, searchDepth, treasureCoords:tuple[int,int], startPosition=Position((0, 3), Facing.UP)):
        super().__init__(name, searchDepth, startPosition)
        self.agendaKey = (lambda x: abs(x[1].coords[0]-treasureCoords[0]) + abs(x[1].coords[1]-treasureCoords[1]) if self.innerWorld.agentAvatar.treasure==0 else abs(x[1].coords[0]-startPosition.coords[0]) + abs(x[1].coords[1]-startPosition.coords[1])) #manhattan distance to treasure, then manhattan distance to exit
