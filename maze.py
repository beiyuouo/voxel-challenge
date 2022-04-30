from scene import Scene
import taichi as ti
from taichi.math import *

scene = Scene(exposure=1)
scene.set_floor(-0.05, (1.0, 1.0, 1.0))
scene.set_background_color((1.0, 0, 0))

height, width = 15, 15

u_parent = [_ for _ in range(height * width)]


def find(x):
    if u_parent[x] == x:
        return x
    else:
        u_parent[x] = find(u_parent[x])
    return u_parent[x]


def union(x, y):
    x, y = find(x), find(y)
    if x != y:
        u_parent[x] = y


def generate_maze(height, width, start_pos, end_pos):
    maze_ = [[[0, 0, 0] for _ in range(width)] for _ in range(height)]
    # maze_[start_pos[0]][start_pos[1]][0] = 0
    # maze_[end_pos[0]][end_pos[1]][0] = 0
    wall_set = []
    for i in range(height):
        for j in range(width):
            if i + 1 < height:
                wall_set.append((i, j, 1))
            if j + 1 < width:
                wall_set.append((i, j, 2))

    _x, _y = 0, 345
    for i in range(1000):
        _x, _y = (_x + 2333333) % len(wall_set), (_y + 2333333) % len(wall_set)
        if _x != _y:
            wall_set[_x], wall_set[_y] = wall_set[_y], wall_set[_x]
    print(wall_set)
    while len(wall_set) > 0:
        pos = wall_set.pop()
        x1, y1 = pos[0], pos[1]
        if pos[2] == 1:
            x2, y2 = x1 + 1, y1
        else:
            x2, y2 = x1, y1 + 1
        if find(x1 * width + y1) != find(x2 * width + y2):
            union(x1 * width + y1, x2 * width + y2)
        else:
            maze_[x1][y1][pos[2]] = 1
    return maze_


maze_ = generate_maze(height, width, (0, 0), (width - 1, height - 1))
for _ in maze_:
    print(_)

maze = ti.Vector.field(3, ti.i32, (height, width))
for i in range(height):
    for j in range(width):
        maze[i, j] = maze_[i][j]


@ti.func
def build_wall(pos, dir, len, color, color_noise):
    for i in range(len):
        scene.set_voxel(pos + dir * i, 1, color + color_noise * ti.random())


@ti.kernel
def initialize_voxels():
    for i, j in ti.ndrange(height, width):
        scene.set_voxel(vec3(i * 2, 1, j * 2), 2, vec3(1, 1, 1))
        if maze[i, j][1] == 1:
            scene.set_voxel(vec3(i * 2 + 1, 1, j * 2), 1, vec3(0.5, 0.5, 0.5))
        else:
            scene.set_voxel(vec3(i * 2 + 1, 1, j * 2), 1, vec3(1, 1, 1))
        if maze[i, j][2] == 1:
            scene.set_voxel(vec3(i * 2, 1, j * 2 + 1), 1, vec3(0.5, 0.5, 0.5))
        else:
            scene.set_voxel(vec3(i * 2, 1, j * 2 + 1), 1, vec3(1, 1, 1))


initialize_voxels()

scene.finish()
