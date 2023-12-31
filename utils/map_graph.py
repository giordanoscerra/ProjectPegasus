from utils.map import Map
from utils.general import decode

class MapGraph:
    def __init__(self, fullyExploredLevel: Map):
        self.lastVisit = set()
        self.level = fullyExploredLevel
        self.initLastVisit(fullyExploredLevel)
        
    def initLastVisit(self, level: Map):
        map = level.state['screen_descriptions']
        for i in range(len(map)):
            for j in range(len(map[0])):
                description = decode(map[i][j])
                if(description == 'dark part of a room'):
                    self.lastVisit.add((i,j))

    def update(self) -> bool:
        map = self.level.state['screen_descriptions']
        updated = False
        for unvisited in self.lastVisit.copy():
            description = decode(map[unvisited[0]][unvisited[1]])
            if(description != 'dark part of a room'):
                updated = True
                self.lastVisit.discard(unvisited)
        return updated

    def fullVisited(self) -> bool:
        return len(self.lastVisit) == 0

    def print_graph(self):
        print(self.lastVisit)