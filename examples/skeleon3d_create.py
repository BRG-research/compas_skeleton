from compas_skeleton.datastructure import Skeleton3D
from compas_rhino.artists import MeshArtist
from compas.datastructures import mesh_subdivide_catmullclark
import compas_rhino
from compas.datastructures import mesh_weld

# lines = [
#     ([0.0, 0.0, 0.0], [0.0, 10.0, 0.0]),
#     ([0.0, 0.0, 0.0], [-8.6, -5.0, 0.0]),
#     ([0.0, 0.0, 0.0], [8.6, -5.0, 0.0])
#     ]

guids = compas_rhino.select_lines()
lines = compas_rhino.get_line_coordinates(guids)

sk3 = Skeleton3D.from_skeleton_lines(lines)
sk3.section_seg = 4
sk3.branch_radius = 2
sk3.node_radius_fac = 1.5
sk3.generate_mesh()
sk3.merge_triangles()
# print(sk3._merge_close_nodes())
# print(sk3.nodes_joint)
# sk3 = mesh_subdivide_catmullclark(sk3, 3)

artist = MeshArtist(sk3)
guid = artist.draw_faces(join_faces=True)
