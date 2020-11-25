import compas_rhino
from compas_skeleton.datastructure import Skeleton3D_Node
from compas_rhino.artists import MeshArtist

guids = compas_rhino.select_lines()
lines = compas_rhino.get_line_coordinates(guids)

sk3_node = Skeleton3D_Node.from_skeleton_lines(lines)
sk3_node.joint_width = 2
sk3_node.leaf_width = 2
sk3_node.update_vertices_location()
sk3_node.to_json('../data/sk3_node.json', pretty=True)

artist = MeshArtist(sk3_node)
artist.draw_mesh()
