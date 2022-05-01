from cmath import sin
from scene import Scene
import taichi as ti
from taichi.math import *

scene = Scene(exposure=1, voxel_edges=0)
scene.set_floor(-0.5, (1.0, 1.0, 1.0))
scene.set_background_color((1.0, 1.0, 1.0))
scene.set_directional_light((1, 1, 1), 1, (1.0, 1.0, 1.0))


@ti.func
def set_color_voxel(pos, mat, color, color_noise, prob=1):
    if ti.random() > prob:
        scene.set_voxel(pos, mat, color - color_noise)
    else:
        scene.set_voxel(pos, mat, color)


@ti.func
def build_fortress(pos, sz1, sz2, height, color, color_noise):
    for x, y in ti.ndrange((-sz1, sz1 + 1), (-sz2, sz2 + 1)):
        if x == -sz1 or x == sz1 or y == -sz2 or y == sz2:
            for z in range(height):
                set_color_voxel(pos + vec3(x, z, y), 1, color, color_noise, 0.8)
            if (x + y) % 4 == 0 or (x + y) % 4 == 1:
                set_color_voxel(pos + vec3(x, height, y), 1, color, color_noise)
        set_color_voxel(pos + vec3(x, height - 2, y), 1, color, color_noise, 0.8)


@ti.func
def build_block(pos1, pos2, color, color_noise, prob=1, mat=1):
    x_min, y_min, z_min = min(pos1.x, pos2.x), min(pos1.y, pos2.y), min(pos1.z, pos2.z)
    x_max, y_max, z_max = max(pos1.x, pos2.x), max(pos1.y, pos2.y), max(pos1.z, pos2.z)
    for x, y, z in ti.ndrange((x_min, x_max + 1), (y_min, y_max + 1), (z_min, z_max + 1)):
        set_color_voxel(vec3(x, y, z), mat, color, color_noise, prob)


@ti.func
def build_door(pos, height, radius, color, color_noise, prob=1, mat=1):
    for x, z in ti.ndrange((-radius, radius + 1), (-radius, radius + 1)):
        if ti.sqrt(x * x + z * z) - 0.8 <= radius:
            set_color_voxel(pos + vec3(x, z, 0), mat, color, color_noise, prob)
    for x, z in ti.ndrange((-radius, radius + 1), (-height, 1)):
        set_color_voxel(pos + vec3(x, z, 0), mat, color, color_noise, prob)


@ti.func
def build_fire(pos):
    scene.set_voxel(pos, 1, (1, 0, 0))
    scene.set_voxel(pos + vec3(0, 1, 0), 1, (1, 1, 0))


@ti.kernel
def initialize_voxels():
    d_ = 15
    build_fortress(vec3(0, 0, 0), 8, 8, 20, vec3(0.95, 0.98, 0.9), vec3(0.15))
    build_fortress(vec3(-d_, 0, -d_), 4, 4, 15, vec3(0.95, 0.98, 0.9), vec3(0.15))
    build_fortress(vec3(d_, 0, -d_), 4, 4, 15, vec3(0.95, 0.98, 0.9), vec3(0.15))
    build_fortress(vec3(-d_, 0, d_), 4, 4, 15, vec3(0.95, 0.98, 0.9), vec3(0.15))
    build_fortress(vec3(d_, 0, d_), 4, 4, 15, vec3(0.95, 0.98, 0.9), vec3(0.15))

    build_fortress(vec3(0, 0, -d_), d_, 2, 13, vec3(0.95, 0.98, 0.9), vec3(0.15))
    build_fortress(vec3(0, 0, d_), d_, 2, 13, vec3(0.95, 0.98, 0.9), vec3(0.15))
    build_fortress(vec3(-d_, 0, 0), 2, d_, 13, vec3(0.95, 0.98, 0.9), vec3(0.15))
    build_fortress(vec3(d_, 0, 0), 2, d_, 13, vec3(0.95, 0.98, 0.9), vec3(0.15))

    for i in ti.ndrange((d_ - 2, d_ + 3)):
        build_door(vec3(0, 6, i), 6, 4, vec3(0.6, 0.6, 0.6), vec3(0))
        build_door(vec3(0, 5, i), 5, 3, vec3(0, 0, 0), vec3(0), 1, 0)
    build_door(vec3(0, 5, d_), 5, 3, vec3(0.43, 0.352, 0.156), vec3(0))

    build_door(vec3(-d_, 8, d_ + 4), 2, 2, vec3(0.95, 0.98, 0.9), vec3(0), 1, 0)
    build_door(vec3(-d_, 8, d_ + 3), 2, 2, vec3(0.95, 0.98, 0.9), vec3(0), 1, 1)
    build_door(vec3(d_, 8, d_ + 4), 2, 2, vec3(0.95, 0.98, 0.9), vec3(0), 1, 0)
    build_door(vec3(d_, 8, d_ + 3), 2, 2, vec3(0.95, 0.98, 0.9), vec3(0), 1, 1)

    build_block(vec3(-d_ - 9, -1, -d_ - 9), vec3(d_ + 9, -1, d_ + 9), vec3(0.85, 1, 0.44),
                vec3(0.1), 0.8)
    build_block(vec3(-d_ - 9, -2, -d_ - 9), vec3(d_ + 9, -2, d_ + 9), vec3(0.58, 0.5, 0.31),
                vec3(0.03), 0.8)
    build_block(vec3(-4, -1, d_ - 2), vec3(4, -1, d_ + 9), vec3(0.6, 0.6, 0.6), vec3(0.03), 0.8)


initialize_voxels()
scene.finish()