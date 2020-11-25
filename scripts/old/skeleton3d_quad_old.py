from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from compas.datastructures import Mesh
from compas.datastructures import Network
from compas.datastructures import mesh_smooth_centroid
from compas.datastructures import mesh_subdivide_catmullclark
from compas.datastructures import mesh_subdivide_quad
from compas.geometry import convex_hull
from compas.geometry import Vector
from compas.geometry import add_vectors
from compas.geometry import cross_vectors
from compas.geometry import Plane
from compas.geometry import project_point_plane
from compas.geometry import angle_vectors
from compas.geometry.transformations import mirror_points_plane
from compas.topology import unify_cycles
from compas.utilities import flatten
from compas.utilities import pairwise
from compas.utilities import geometric_key
from compas.utilities import reverse_geometric_key

import compas_rhino
from compas_rhino.artists import MeshArtist

import copy
import math


__all__ = ['Skeleton3D_Node']


def get_convex_hull_mesh(points):
    faces = convex_hull(points)
    vertices = list(set(flatten(faces)))
    vertices_index = vertices

    i_index = {i: index for index, i in enumerate(vertices)}
    vertices = [points[index] for index in vertices]
    faces = [[i_index[i] for i in face] for face in faces]
    faces = unify_cycles(vertices, faces)

    mesh = Mesh.from_vertices_and_faces(vertices, faces)

    return mesh, vertices_index


def _vec_unitize(vec):
    """ untinize a vec represented by a list """
    vec_unitized = Vector(*vec).unitized()
    return [vec_unitized.x, vec_unitized.y, vec_unitized.z]


def _vecs_unitize(vecs):
    """ untinize a list of vectors """
    return [_vec_unitize(vec) for vec in vecs]


def _equal_angle_vector(vectors):
    """calculate the vector which has same angle with each of the 3 input vectors

    """
    if len(vectors) != 3:
        print('it takes a list of 3 vectors as argument!')
        return

    pts = _vecs_unitize(vectors)
    vecs = []
    for sp, ep in pairwise(pts):
        vecs.append(Vector.from_start_end(sp, ep))

    return cross_vectors(vecs[0], vecs[1])


class Skeleton3D_Node(Mesh):

    def __init__(self):
        super(Skeleton3D_Node, self).__init__()
        # self.branches = []
        self.pt_center = None
        # self.descendent_tree = {}
        self.joint_width = 3
        self.leaf_width = 2
        self.network_convexhull = {}
        # self.leaf_width = []
        self.attributes.update({
            'network': None
            'convexhull_mesh': None
            'descendent_tree': None
        })

    # --------------------------------------------------------------------------
    # special attributes
    # --------------------------------------------------------------------------

    @property
    def network(self):
        return self.attributes['network']

    @network.setter
    def network(self, network):
        self.attributes['network'] = network

    @property
    def convexhull_mesh(self):
        return self.attributes['convexhull_mesh']

    @convexhull_mesh.setter
    def convexhull_mesh(self, mesh):
        self.attributes['convexhull_mesh'] = mesh

    @property
    def descendent_tree(self):
        return self.attributes['descendent_tree']

    # --------------------------------------------------------------------------
    # constructors
    # --------------------------------------------------------------------------

    @classmethod
    def from_skeleton_lines(cls, lines=[]):
        sk3_node = cls()

        network = Network.from_lines(lines)
        sk3_node._from_network(network)

        return sk3_node

    @classmethod
    def from_network(cls, network=None):
        sk3_node = cls()
        sk3_node._from_network(network)

        return sk3_node

    # --------------------------------------------------------------------------
    # constructors
    # --------------------------------------------------------------------------

    def _from_network(self, network):
        # network should only have one joint to create a skeleton3d node
        self.network = network
        leafs = []
        joints = []
        for key in network.node:
            if network.is_leaf(key):
                leafs.append(key)
            else:
                joints.append(key)

        if len(joints) != 1:
            print('only one joint node is allowed to make a skeleton3d node!')
            return

        # make a convexhull mesh, copy its halfedge dictionary \
        # as descendent tree of the skeleton3d node
        self.pt_center = network.node_coordinates(joints[0])
        pts_leaf = [network.node_coordinates(key) for key in leafs]

        input_keys = leafs
        convex_hull_mesh = get_convex_hull_mesh(pts_leaf)[0]
        output_keys = get_convex_hull_mesh(pts_leaf)[1]

        self.network_convexhull = dict(zip(input_keys, output_keys))

        self.attributes.update({
            'descendent_tree': copy.deepcopy(convex_hull_mesh.halfedge)
        })

        for u, v in convex_hull_mesh.edges():
            self.attributes['descendent_tree'][u][v] = {'jp': None, 'lp': None}
            self.attributes['descendent_tree'][v][u] = {'jp': None, 'lp': None}

        # for each convex hall mesh face, find a point as the intersection
        # add this point as 'jp' to each edge of descendent tree
        current_key = 0
        for fkey in convex_hull_mesh.faces():

            face = convex_hull_mesh.face[fkey]
            vecs_join_to_leaf = [
                Vector.from_start_end(
                    self.pt_center, convex_hull_mesh.vertex_coordinates(v)
                    )
                for v in face
                ]

            vecs_join_to_leaf = _vecs_unitize(vecs_join_to_leaf)
            vec_joint_to_face = _equal_angle_vector(vecs_join_to_leaf)

            vec = Vector(*vec_joint_to_face)
            vec.unitize()
            vec.scale(self.joint_width)

            pt = add_vectors(self.pt_center, vec)

            v_keys = face + [face[0]]
            for u, v in pairwise(v_keys):
                self.attributes['descendent_tree'][u][v].update({'jp': current_key})

            self.add_vertex(current_key)
            self.vertex[current_key].update({'x': pt[0], 'y': pt[1], 'z': pt[2]})

            current_key += 1

        # add 'lp' to each edge of descendent tree
        for key in convex_hull_mesh.vertices():
            nbrs = convex_hull_mesh.vertex_neighbors(key)
            for nbr in nbrs:
                pt_joint_descendent = self.vertex_coordinates(self.descendent_tree[key][nbr]['jp'])

                vec_edge = Vector.from_start_end(self.pt_center, convex_hull_mesh.vertex_coordinates(key))
                pln_end = Plane(convex_hull_mesh.vertex_coordinates(key), vec_edge)
                pt = project_point_plane(pt_joint_descendent, pln_end)
                vec_leaf = Vector.from_start_end(convex_hull_mesh.vertex_coordinates(key), pt)
                vec_leaf.unitize()
                vec_leaf.scale(self.leaf_width)
                pt = add_vectors(convex_hull_mesh.vertex_coordinates(key), vec_leaf)

                self.attributes['descendent_tree'][key][nbr].update({'lp': current_key})

                self.add_vertex(current_key)
                self.vertex[current_key].update({'x': pt[0], 'y': pt[1], 'z': pt[2]})

                current_key += 1

        # add mesh faces
        for key in convex_hull_mesh.vertices():
            nbrs = convex_hull_mesh.vertex_neighbors(key, ordered=True)
            v_keys = nbrs + [nbrs[0]]
            for a, b in pairwise(v_keys):
                face = [
                    self.descendent_tree[key][a]['lp'],
                    self.descendent_tree[key][a]['jp'],
                    self.descendent_tree[key][b]['jp'],
                    self.descendent_tree[key][b]['lp']
                ]
                self.add_face(face)


if __name__ == '__main__':
    pass
