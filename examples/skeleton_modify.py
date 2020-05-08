import os
from compas_skeleton.datastructure import Skeleton
from compas_skeleton.rhino import SkeletonObject
from compas_skeleton.rhino import SkeletonArtist

try:
    HERE = os.path.dirname(__file__)
except NameError:
    HERE = os.getcwd()

DATA = os.path.join(HERE, '../data')
FILE = os.path.join(DATA, 'skeleton.json')

# ==============================================================================
# Load skeleton from file
# ==============================================================================

skeleton = Skeleton.from_json(FILE)
# print(skeleton.vertex_attribute(8, 'transform'))
skeletonobject = SkeletonObject(skeleton)
skeletonobject.draw()
skeletonobject.update()

"""
following functions are available:
    'm_skeleton'
    'm_mesh'
    'leaf_width'
    'node_width'
    'leaf_extend'
    'subdivide'
    'merge'
    'add_lines'
    'remove_lines'
    'finish'
"""

# ==============================================================================
# Export
# ==============================================================================

skeletonobject.datastructure.to_json(FILE, pretty=True)
