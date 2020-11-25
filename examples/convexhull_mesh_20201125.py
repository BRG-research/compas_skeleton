import compas_rhino
from compas.datastructures import Network
from compas.datastructures import Mesh
from compas.datastructures import mesh_subdivide_catmullclark
from compas.datastructures import mesh_subdivide_quad
from compas.utilities import geometric_key
from compas.utilities import reverse_geometric_key
from compas.datastructures import meshes_join
from compas.datastructures import meshes_join_and_weld
from compas.geometry import closest_point_in_cloud
from compas.geometry import convex_hull
from compas.geometry import add_vectors
from compas.topology import unify_cycles
from compas.utilities import flatten
from compas.utilities import pairwise
from compas_skeleton.datastructure import Skeleton3D_Node
from compas_rhino.artists import MeshArtist

import compas_rhino
from compas_skeleton.datastructure import Skeleton3D_Node
from compas_rhino.artists import MeshArtist



def get_convex_hull_mesh(points):
    faces = convex_hull(points)
    vertices = list(set(flatten(faces)))

    i_index = {i: index for index, i in enumerate(vertices)}
    vertices = [points[index] for index in vertices]
    faces = [[i_index[i] for i in face] for face in faces]
    faces = unify_cycles(vertices, faces)

    mesh = Mesh.from_vertices_and_faces(vertices, faces)

    return mesh

guids = compas_rhino.select_lines()
lines = compas_rhino.get_line_coordinates(guids)

network = Network.from_lines(lines)
joints = []
leafs = []
for key in network.node:
    if network.is_leaf(key):
        leafs.append(key)
    else:
        joints.append(key)

points = []
for key in leafs:
    points.append(network.node_coordinates(key))

mesh = get_convex_hull_mesh(points)
print(mesh)
artist = MeshArtist(mesh)
artist.draw_mesh()