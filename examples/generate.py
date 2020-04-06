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

guids = compas_rhino.select_lines()
lines = compas_rhino.get_line_coordinates(guids)
compas_rhino.rs.HideObjects(guids)

skeleton = Skeleton.from_skeleton_lines(lines)
skeletonobject = SkeletonObject(skeleton)
skeletonobject.draw()
skeletonobject.dynamic_update_mesh()

# ==============================================================================
# Export
# ==============================================================================

skeletonobject.datastructure.to_json(FILE, pretty=True)
