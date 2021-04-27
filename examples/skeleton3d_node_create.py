import compas_rhino
from compas_skeleton.datastructure import Skeleton3D_Node
from compas_rhino.artists import MeshArtist
from compas.datastructures import mesh_subdivide_catmullclark
from compas.datastructures import mesh_subdivide_quad
from compas.datastructures import Mesh
from compas.datastructures import mesh_collapse_edge

from copy import deepcopy


def mesh_fast_copy(other):
    subd = Mesh()
    subd.vertex = deepcopy(other.vertex)
    subd.face = deepcopy(other.face)
    subd.facedata = deepcopy(other.facedata)
    subd.halfedge = deepcopy(other.halfedge)
    subd._max_face = other._max_face
    subd._max_vertex = other._max_vertex
    return subd

guids = compas_rhino.select_lines()
lines = compas_rhino.get_line_coordinates(guids)

sk3_node = Skeleton3D_Node.from_skeleton_lines(lines)
<<<<<<< Updated upstream
sk3_node.joint_width = 0.8
sk3_node.leaf_width = 0.2
=======
sk3_node.joint_width = 1
sk3_node.leaf_width = 1
>>>>>>> Stashed changes
sk3_node.update_vertices_location()
sk3_node = mesh_fast_copy(sk3_node)
sk3_node.to_json('../data/sk3_node.json', pretty=True)

# fixed = list(sk3_node.vertices_where({'vertex_degree': 3}))
# sk3_node = mesh_subdivide_catmullclark(sk3_node, k=1, fixed=fixed)
# sk3_node = mesh_subdivide_quad(sk3_node, k=1)

# def draw_mesh_faces(mesh):
#     fkeys_nodraw = [fkey for fkey in mesh.faces() if mesh.face_area(fkey) <= 0]
#     fkeys = list(set(list(mesh.faces())) - set(fkeys_nodraw))

#     artist = MeshArtist(mesh)
#     artist.draw_faces(faces=fkeys, join_faces=True)

# draw_mesh_faces(sk3_node)
artist = MeshArtist(sk3_node)
artist.draw_mesh()