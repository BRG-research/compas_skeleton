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
# from compas.geometry import convex_hull
from compas.geometry import add_vectors
from compas.topology import unify_cycles
from compas.utilities import flatten
from compas.utilities import pairwise
# from compas_skeleton.datastructure import Skeleton3D_Node
from compas_rhino.artists import MeshArtist
from compas.geometry import cross_vectors
from compas.geometry import subtract_vectors
from compas.geometry import dot_vectors
from compas.geometry import cross_vectors_xy

import compas_rhino
# from compas_skeleton.datastructure import Skeleton3D_Node
from compas_rhino.artists import MeshArtist
from compas.utilities import geometric_key
from compas.utilities import reverse_geometric_key
from copy import deepcopy

def has_face(face, target_face):
    face_copy = deepcopy(face)
    face_copy.sort()
    target_face_copy = deepcopy(target_face)
    target_face_copy.sort()

    return face_copy == target_face_copy


def convex_hull(points, constraints):
    """Construct convex hull for a set of points.

    """
    def _normal_face(face):
        u = subtract_vectors(points[face[1]], points[face[0]])
        v = subtract_vectors(points[face[-1]], points[face[0]])
        return cross_vectors(u, v)

    def _seen(face, p):
        normal = _normal_face(face)
        vec = subtract_vectors(points[p], points[face[0]])
        return (dot_vectors(normal, vec) >= 0)

    def _bdry(faces):
        bdry_fw = set([(face[i - 1], face[i]) for face in faces for i in range(len(face))])
        bdry_bk = set([(face[i], face[i - 1]) for face in faces for i in range(len(face))])
        return bdry_fw - bdry_bk

    def _add_point(hull, p):
        seen_faces = [face for face in hull if _seen(face, p)]
        seen_faces = [face for face in seen_faces if not has_face(face, constraints)]

        if len(seen_faces) == len(hull):
            # if can see all faces, unsee ones looking "down"
            normal = _normal_face(seen_faces[0])
            seen_faces = [face for face in seen_faces if dot_vectors(_normal_face(face), normal) > 0]

        for face in seen_faces:
            hull.remove(face)

        for edge in _bdry(seen_faces):
            hull.append([edge[0], edge[1], p])

    hull = [[0, 1, 2], [0, 2, 1]]
    for i in range(3, len(points)):
        _add_point(hull, i)
    return hull


def get_convex_hull_mesh(points, constraints):
    faces = convex_hull(points, constraints)
    vertices = list(set(flatten(faces)))

    i_index = {i: index for index, i in enumerate(vertices)}
    vertices = [points[index] for index in vertices]
    faces = [[i_index[i] for i in face] for face in faces]
    faces = unify_cycles(vertices, faces)

    mesh = Mesh.from_vertices_and_faces(vertices, faces)

    return mesh

# guids = compas_rhino.select_lines()
# lines = compas_rhino.get_line_coordinates(guids)

# network = Network.from_lines(lines)
# joints = []
# leafs = []
# for key in network.node:
#     if network.is_leaf(key):
#         leafs.append(key)
#     else:
#         joints.append(key)

# points = []
# for key in leafs:
#     points.append(network.node_coordinates(key))

guids = compas_rhino.select_points('select points')
points = compas_rhino.get_point_coordinates(guids)
compas_rhino.rs.Redraw()

# test_points_guids = compas_rhino.select_points('select constraints')
test_points_guids = compas_rhino.rs.GetPoints('select constraints')
# test_points = compas_rhino.get_point_coordinates(test_points_guids)
test_points = [[point.X, point.Y, point.Z] for point in test_points_guids]
test_points_gkeys = [geometric_key(xyz) for xyz in test_points]
gkeys = [geometric_key(xyz) for xyz in points]

face = []
for gkey in test_points_gkeys:
    face.append(gkeys.index(gkey))

constraints = face
print('constrants: {}'.format(constraints))

mesh = get_convex_hull_mesh(points, constraints)
artist = MeshArtist(mesh)
artist.draw_mesh()