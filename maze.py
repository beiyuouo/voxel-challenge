from scene import Scene
import taichi as ti
from taichi.math import *

scene = Scene(exposure=1)
scene.set_floor(-0.05, (1.0, 1.0, 1.0))
scene.set_background_color((1.0, 0, 0))


class DisjointSet(object):

    def __init__(self, n):
        self.parent = [0 for _ in range(n)]
        for i in range(n):
            self.parent[i] = i

    def find(self, x):
        if self.parent[x] == x:
            return x
        else:
            self.parent[x] = self.find(self.parent[x])
            return self.parent[x]

    def union(self, x, y):
        x, y = self.find(x), self.find(y)
        if x != y:
            self.parent[x] = y


def generate_maze(height, width, start_pos, end_pos):
    maze_ = [[1 for _ in range(width)] for _ in range(height)]
    maze_[start_pos[0]][start_pos[1]] = 0
    maze_[end_pos[0]][end_pos[1]] = 0
    dirs = [(0, 1), (1, 0), (0, -1), (-1, 0)]

    union_set = DisjointSet(width * height)
    wall_set = set()
    for i in range(height):
        for j in range(width):
            if maze_[i][j] == 1:
                wall_set.add((i, j))

    while len(wall_set) > 0:
        pos = wall_set.pop()
        abled = []
        for dir in dirs:
            pos_ = (pos[0] + dir[0], pos[1] + dir[1])
            if pos_[0] < 0 or pos_[0] >= height or pos_[1] < 0 or pos_[1] >= width:
                continue
            abled.append((pos_, union_set.find(pos_[0] * width + pos_[1])))
        if len(abled) <= 1:
            continue
        for i in range(1, len(abled)):
            if union_set.find(abled[i][1]) != union_set.find(abled[0][1]):
                union_set.union(abled[i][1], abled[0][1])
                maze_[pos[0]][pos[1]] = 0

    return maze_


maze = generate_maze(10, 10, (0, 0), (9, 9))
for _ in maze:
    print(_)
