from scene import Scene
import taichi as ti
from taichi.math import *
scene = Scene(exposure=1, voxel_edges=0.0)
scene.set_directional_light((-0.3, 1, 1), 0.1, (0.5, 1, 0.5))
scene.set_floor(0, vec3(223,233,169) / 255.0);scene.set_background_color((0.3, 0.4, 0.6))
col_g = vec3(152, 228, 38) / 255.0;col_gd = vec3(69, 172, 14) / 255.0;col_gdd = vec3(55, 144, 2) / 255.0
col_f1 = vec3(19, 186, 27) / 255.0;col_f2 = vec3(3, 157, 22) / 255.0;col_f3 = vec3(14, 164, 25) / 255.0
col_f4 = vec3(4, 134, 22) / 255.0
@ti.func
def create_ball(p, r, mat, color):
    for x, y, z in ti.ndrange((-r, r + 1), (-r, r + 1), (-r, r + 1)):
        if x * x + y * y + z * z <= r * r - 0.1: scene.set_voxel(p + vec3(x, y, z), mat, color)
@ti.func
def create_box(p, sx, sy, sz, mat, color):
    for x, y, z in ti.ndrange((0, sx), (0, sy), (0, sz)):
        scene.set_voxel(p + vec3(x, z, y), mat, color)
@ti.func
def create_circle(p, r_: ti.float32, mat, color, static_axis=0, eps=1):
    r = ti.cast(ti.ceil(r_), ti.int32)
    if static_axis == 0:
        for y, z in ti.ndrange((-r, r + 1), (-r, r + 1)):
            if y * y + z * z <= r * r + eps: scene.set_voxel(p + vec3(0, z, y), mat, color)
    elif static_axis == 1:
        for x, z in ti.ndrange((-r, r + 1), (-r, r + 1)):
            if x * x + z * z <= r * r + eps: scene.set_voxel(p + vec3(x, z, 0), mat, color)
    elif static_axis == 2:
        for x, y in ti.ndrange((-r, r + 1), (-r, r + 1)):
            if x * x + y * y <= r * r + eps: scene.set_voxel(p + vec3(x, 0, y), mat, color)
@ti.func
def create_sine_curve(p, A, l, mat, color, dir1=vec3(0, 1, 0), dir2=vec3(0, 0, 1), tk=1):
    for x, tx in ti.ndrange((0, l + 1), (0, tk)):
        y = ti.cast(A * ti.sin(1.0 * x / l * ti.math.pi), ti.int32)
        scene.set_voxel(p + y * dir2 + tx * dir2 + x * dir1, mat, color)
@ti.func
def create_line(p, l, mat, color, dir1=vec3(0, 1, 0), step=1):
    for x in ti.ndrange((0, l + 1)):
        scene.set_voxel(p + x * dir1 * step, mat, color)
@ti.func
def create_eye(p):
    create_box(p, 2, 8, 3, 0, vec3(0))
    create_box(p, 2, 1, 3, 1, vec3(0))
    create_box(p + vec3(0, 1, 0), 1, 1, 1, 1, vec3(1))
@ti.func
def create_leaf(p, r, dir, mat, color):
    if dir == 1:
        for x, y in ti.ndrange((0, r + 1), (0, r + 1)):
            if x * x + y * y <= r * r and (r - x) * (r - x) + (r - y) * (r - y) <= r * r:
                z = ti.cast(ti.floor(1 * ti.sin(ti.math.pi * x / r) + ti.sin(ti.math.pi * y / r)), ti.int32)
                scene.set_voxel(p + vec3(x, z, y), mat, color)
    elif dir == 2:
        for x, y in ti.ndrange((0, r + 1), (0, r + 1)):
            if x * x + (r - y) * (r - y) <= r * r and (r - x) * (r - x) + y * y <= r * r:
                z = ti.cast(ti.floor(1 * ti.sin(ti.math.pi * x / r) + ti.sin(ti.math.pi * y / r)), ti.int32)
                scene.set_voxel(p + vec3(x, z, y), mat, color)
@ti.func
def create_peashooter(p):
    create_ball(p + vec3(0, 18, 0), 8, 1, col_g)
    for i in range(6):
        create_circle(p + vec3(0, 16, 6 + i), 3.0, 1, col_g, 1)
    create_circle(p + vec3(0, 16, 12), 4.0, 1, col_g, 1);create_circle(p + vec3(0, 16, 13), 4.0, 1, col_g, 1)
    for i in range(8):
        create_circle(p + vec3(0, 16, 6 + i), ti.max(2.0, ti.min(i - 3.0, 3.0)), 0, col_g, 1)
    for x, y in ti.ndrange((-1, 1 + 1), (-1, 1 + 1)):
        create_sine_curve(p + vec3(x, 5, y), 2, 5, 1, col_gd, vec3(0, 1, 0), vec3(0, 0, -1))
        create_sine_curve(p + vec3(x, 0, y), 2, 5, 1, col_gd, vec3(0, 1, 0), vec3(0, 0, 1))
    create_sine_curve(p + vec3(0, 24, -5), 2, 5, 1, col_gd, vec3(0, 0, -1), vec3(0, 1, 0), 2)
    create_eye(p + vec3(-3, 20, 5));create_eye(p + vec3(2, 20, 5))
    create_leaf(p + vec3(0, 0, -6), 6, 1, 1, col_gdd);create_leaf(p + vec3(-7, 0, 1), 6, 1, 1, col_gdd)
    create_leaf(p + vec3(-6, 0, -6), 6, 2, 1, col_gdd);create_leaf(p + vec3(1, 0, 1), 6, 2, 1, col_gdd)
@ti.func
def create_grass(p, sx, sy, sz, mat, color):
    create_box(p, sx, sy, sz, mat, color)
    for x, y in ti.ndrange((0, sx + 1), (0, sy + 1)):
        if ti.random() > 0.8:
            scene.set_voxel(p + vec3(0, 0, (ti.random() - 0.5) * 4), mat, color)
            scene.set_voxel(p + vec3(x, 0, (ti.random() - 0.5) * 4), mat, color)
            scene.set_voxel(p + vec3((ti.random() - 0.5) * 4, 0, y), mat, color)
            scene.set_voxel(p + vec3((ti.random() - 0.5) * 4, 0, 0), mat, color)
@ti.kernel
def initialize_voxels():
    for x in ti.ndrange((-3, 3)):
        if ti.random() < 0.5:
            create_peashooter(vec3(x * 20 + 10, 2, -63 + 12))
            create_ball(vec3(x * 20 + 10, 16, ti.random() * 60), 3, 1, col_g)
        else:
            create_peashooter(vec3(x * 20 + 10, 2, -43 + 12))
            create_ball(vec3(x * 20 + 10, 16, ti.random() * 60), 3, 1, col_g)
    for x, y in ti.ndrange((-3, 3), (-3, 3)):
        if x % 2 == 0 and y % 2 == 0:
            create_grass(vec3(20 * x, 0, 20 * y), 20, 20, 1, 1, col_f3)
        elif x % 2 == 0 and y % 2 == 1:
            create_grass(vec3(20 * x, 0, 20 * y), 20, 20, 1, 1, col_f4)
        elif x % 2 == 1 and y % 2 == 0:
            create_grass(vec3(20 * x, 0, 20 * y), 20, 20, 1, 1, col_f1)
        elif x % 2 == 1 and y % 2 == 1:
            create_grass(vec3(20 * x, 0, 20 * y), 20, 20, 1, 1, col_f2)
initialize_voxels()
scene.finish()