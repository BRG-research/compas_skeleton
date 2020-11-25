from compas_skeleton.datastructure import Skeleton3D
from compas_rhino.artists import MeshArtist
from compas.datastructures import mesh_subdivide_catmullclark
import compas_rhino

# lines = [
#     ([0.0, 0.0, 0.0], [0.0, 10.0, 0.0]),
#     ([0.0, 0.0, 0.0], [-8.6, -5.0, 0.0]),
#     ([0.0, 0.0, 0.0], [8.6, -5.0, 0.0])
#     ]

guids = compas_rhino.select_lines()
lines = compas_rhino.get_line_coordinates(guids)

sk3 = Skeleton3D.from_skeleton_lines(lines)
sk3.section_seg = 4
sk3.branch_radius = 1
sk3.node_radius_fac = 2
sk3.generate_mesh()
sk3.merge_triangles()

# mesh = mesh_subdivide_catmullclark(sk3, 1)

artist = MeshArtist(sk3)
artist.draw_faces(join_faces=True)
