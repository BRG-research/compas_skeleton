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

guids = compas_rhino.select_points()
point = compas_rhino.get_point_coordinates(guids)[0]

compas_rhino.rs.HideObjects(guids)

skeleton = Skeleton.from_center_point(point)
skeletonobject = SkeletonObject(skeleton)
skeletonobject.draw()
skeletonobject.dynamic_draw_widths()

# ==============================================================================
# Export
# ==============================================================================

skeletonobject.datastructure.to_json(FILE, pretty=True)
