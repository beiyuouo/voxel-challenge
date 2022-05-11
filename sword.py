from scene import Scene
import taichi as ti
from taichi.math import *

scene = Scene(exposure=1, voxel_edges=0.0)
# scene.set_directional_light((-1, 1, 1), 0.1, (1, 1, 1))
# scene.set_background_color((0.3, 0.4, 0.6))


@ti.kernel
def initialize_voxels():
    pass


initialize_voxels()

scene.finish()
