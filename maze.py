from scene import Scene
import taichi as ti
from taichi.math import *

scene = Scene(exposure=1)
scene.set_floor(-0.05, (1.0, 1.0, 1.0))
scene.set_background_color((1.0, 0, 0))

height, width = 10, 10
maze = ti.field(dtype=ti.i32, shape=(height, width))
u_parent = ti.field(dtype=ti.i32, shape=(height * width))
wall_set = ti.field(dtype=ti.i32, shape=(height * width, 2))
dirs = [vec2(0, 1), vec2(1, 0), vec2(0, -1), vec2(-1, 0)]

dirs = ti.Vector.field(2, dtype=ti.f32, shape=(4))
dirs[0], dirs[1], dirs[2], dirs[3] = vec2(0, 1), vec2(1, 0), vec2(0, -1), vec2(-1, 0)

abled = ti.field(dtype=ti.i32, shape=(4, 2))


@ti.func
def get_parent(x):
    if u_parent[x] == x:
        return x
    u_parent[x] = get_parent(u_parent[x])
    return u_parent[x]


@ti.func
def union(x, y):
    u_parent[get_parent(x)] = get_parent(y)


@ti.func
def generate_maze(height, width, start_pos, end_pos):
    maze[start_pos[0], start_pos[1]] = 0
    maze[end_pos[0], end_pos[1]] = 0

    for i in range(height * width):
        u_parent[i] = i

    itr = 0
    for i in range(height):
        for j in range(width):
            if maze[i, j] == 1:
                wall_set[itr, 0], wall_set[itr, 1] = i, j
                itr += 1

    # shuffle
    for i in range(itr):
        x, y = int(ti.random() * itr), int(ti.random() * itr)
        temp = vec2(wall_set[x, 0], wall_set[x, 1])
        wall_set[x, 0], wall_set[x, 1] = wall_set[y, 0], wall_set[y, 1]
        wall_set[y, 0], wall_set[y, 1] = temp.x, temp.y

    for i in range(itr):
        pos = vec2(wall_set[i, 0], wall_set[i, 1])
        itr = 0
        for idx in range(4):
            pos_ = pos + dirs[idx]
            if pos_.x >= 0 and pos_.x < height and pos_.y >= 0 and pos_.y < width:
                abled[itr, 0], abled[itr, 1] = pos_.x, pos_.y
                itr += 1
        if itr > 1:
            for it in range(1, itr):
                if get_parent(abled[it, 0] * width +
                              abled[it, 1]) != get_parent(abled[0, 0] * width + abled[0, 1]):
                    union(abled[it, 0] * width + abled[it, 1], abled[0, 0] * width + abled[0, 1])
                    maze[pos.x, pos.y] = 0


@ti.func
def build_wall(pos, dir, len, color, color_noise):
    for i in range(len):
        scene.set_voxel(pos + dir * i, 1, color + color_noise * ti.random())


@ti.kernel
def initialize_voxels():
    generate_maze(10, 10, (0, 0), (9, 9))
    for i, j in ti.ndrange(10, 10):
        if maze[i][j] == 1:
            scene.set_voxel((i, 1, j), 1, (0, 0, 0))
        else:
            scene.set_voxel((i, 1, j), 1, (1, 1, 1))


initialize_voxels()

scene.finish()
