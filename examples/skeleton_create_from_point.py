from compas_skeleton.datastructure import Skeleton
from compas_skeleton.rhino import SkeletonObject
import compas_rhino
import os

try: 
    HERE = os.path.dirname(__file__)
except NameError:
    HERE = os.getcwd()

DATA = os.path.join(HERE, '../data')
FILE = os.path.join(DATA, 'skeleton.json')

# ==============================================================================
# input from Rhino
# ==============================================================================

# guids = compas_rhino.select_points()
# point = compas_rhino.get_point_coordinates(guids)[0]

# compas_rhino.rs.HideObjects(guids)
point = [0, 0, 0]
skeleton = Skeleton.from_center_point(point)
skeleton.node_width = 6.0
skeleton.update_mesh_vertices_pos()
skeleton.vertex_attribute(0, 'z', 6.0)
skeleton.subdivide(3)
# from compas.datastructures import Mesh
# Mesh.vertex_attribute()
skeletonobject = SkeletonObject(skeleton)
skeletonobject.draw()
# skeletonobject.dynamic_draw_widths()

# ==============================================================================
# Export
# ==============================================================================

skeletonobject.datastructure.to_json(FILE, pretty=True)
