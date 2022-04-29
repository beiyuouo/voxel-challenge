from scene import Scene
import taichi as ti
from taichi.math import *

scene = Scene(exposure=1, voxel_edges=0.0)
# scene.set_directional_light((-1, 1, 1), 0.1, (1, 1, 1))
# scene.set_background_color((0.3, 0.4, 0.6))


@ti.func
def rotate(v, axis, theta):
    c = ti.cos(theta)
    s = ti.sin(theta)
    return v * c + axis * (1 - c) * v.dot(axis) + s * (v.cross(axis))


@ti.func
def create_feed_ball(feed_r, feed_p, feed_color):
    for i, j, k in ti.ndrange((-feed_r, feed_r), (-feed_r, feed_r), (-feed_r, feed_r)):
        x = ivec3(i, j, k)
        if distance(x, vec3(0, 0, 0)) + 0.5 <= feed_r:
            scene.set_voxel(feed_p + vec3(i, j, k), 2, feed_color)


@ti.kernel
def initialize_voxels():
    n = 60
    r = 20
    p_center = vec3(0, n // 2, -n // 2)

    vec_face_to = vec3(0, 0, 1)
    vec_z = vec3(0, 1, 0)
    vec_normal = normalize(cross(vec_face_to, vec_z))

    mouse_angle = pi / 5
    mouse_angle_min = mouse_angle
    mouse_angle_max = mouse_angle
    mouse_angle_cos_min = ti.cos(mouse_angle_min) - 0.05
    mouse_angle_cos_max = ti.cos(mouse_angle_max) + 0.05
    skin_thickness = 0.5

    eye_angle = mouse_angle + pi / 18
    he_angle = pi / 5

    vec_eye_left = rotate(rotate(vec_face_to, vec_normal, -eye_angle), vec_z, he_angle).normalized()
    vec_eye_right = rotate(rotate(vec_face_to, vec_normal, -eye_angle), vec_z,
                           -he_angle).normalized()

    p_eye_left = p_center + vec_eye_left * r
    p_eye_right = p_center + vec_eye_right * r
    eye_size = 4
    for i, j, k in ti.ndrange((-n, n), (-n, n), (-n, n)):
        x = ivec3(i, j, k)
        color = vec3(2, 2, 2)
        # surface
        if distance(x, p_center) < r + skin_thickness and distance(x,
                                                                   p_center) > r - skin_thickness:
            # mouse
            # project to the plane
            vec_mouse = vec3(i, j, k) - p_center
            vec_mouse_projected = vec_mouse - vec_normal * dot(vec_mouse, vec_normal)
            print(vec_mouse_projected)
            # angle to face to
            angle_cos = dot(vec_mouse_projected,
                            vec_face_to) / (vec_mouse_projected.norm() * vec_face_to.norm())
            if angle_cos <= mouse_angle_cos_max:
                color = vec3(1, 1, 0.)
            if distance(vec3(i, j, k), p_eye_left) <= eye_size or distance(
                    vec3(i, j, k), p_eye_right) <= eye_size:
                color = vec3(0.01, 0.01, 0.01)

        elif distance(x, p_center) <= r - skin_thickness:
            # mouse
            # project to the plane
            vec_mouse = vec3(i, j, k) - p_center
            vec_mouse_projected = vec_mouse - vec_normal * dot(vec_mouse, vec_normal)
            angle_cos = dot(vec_mouse_projected,
                            vec_face_to) / (vec_mouse_projected.norm() * vec_face_to.norm())

            if mouse_angle_cos_min <= angle_cos and angle_cos <= mouse_angle_cos_max or vec_mouse_projected.norm(
            ) < 3:
                color = vec3(0.0, 0.0, 0.0)
        if any(color != vec3(2, 2, 2)):
            scene.set_voxel(vec3(i, j, k), 2, color)

    # add feed ball
    feed_r = 4
    feed_color = vec3(1, 1, 1)
    create_feed_ball(feed_r, p_center + vec3(0, 0, r * 2 + feed_r), feed_color)
    create_feed_ball(feed_r, p_center + vec3(0, 0, r * 3 + feed_r * 2), feed_color)


initialize_voxels()

scene.finish()
