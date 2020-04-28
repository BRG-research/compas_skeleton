from compas_skeleton.datastructure import Skeleton
from compas_skeleton.rhino import SkeletonObject
from compas_skeleton.rhino import SkeletonArtist

lines = [
    ([0.0, 0.0, 0.0], [0.0, 10.0, 0.0]),
    ([0.0, 0.0, 0.0], [-8.6, -5.0, 0.0]),
    ([0.0, 0.0, 0.0], [8.6, -5.0, 0.0])
    ]
skeleton = Skeleton.from_skeleton_lines(lines)
skeleton.node_width = 4.0
skeleton.leaf_width = 1.5
skeleton.leaf_extend = -1.0
skeleton.update_mesh_vertices_pos()
skeleton.subdivide(2)

artist = SkeletonArtist(skeleton)
artist.draw()
