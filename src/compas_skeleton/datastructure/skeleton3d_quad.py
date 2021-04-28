from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from compas.datastructures import Mesh
from compas.datastructures import Network
from compas.geometry import convex_hull
from compas.geometry import Vector
from compas.geometry import add_vectors
from compas.geometry import cross_vectors
from compas.geometry import Plane
from compas.geometry import project_point_plane
from compas.topology import unify_cycles
from compas.utilities import flatten
from compas.utilities import pairwise

import copy


__all__ = ['Skeleton3D_Node', 'Skeleton3D_Branch']


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
        self.attributes.update({
            'network': None,
            'convexhull_mesh': None,
            'network_convexhull': {},
            'descendent_tree': {},
            'joint_width': 1,
            'leaf_width': 1,
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
    def network_convexhull(self):
        return self.attributes['network_convexhull']

    @network_convexhull.setter
    def network_convexhull(self, dic):
        self.attributes['network_convexhull'] = dic

    @property
    def descendent_tree(self):
        return self.attributes['descendent_tree']

    @property
    def network_nodes(self):
        joints = []
        leafs = []
        for key in self.network.node:
            if self.network.is_leaf(key):
                leafs.append(key)
            else:
                joints.append(key)

        return joints, leafs

    @property
    def joint_width(self):
        return self.attributes['joint_width']

    @joint_width.setter
    def joint_width(self, width):
        self.attributes['joint_width'] = width

    @property
    def leaf_width(self):
        return self.attributes['leaf_width']

    @leaf_width.setter
    def leaf_width(self, width):
        self.attributes['leaf_width'] = width

    # --------------------------------------------------------------------------
    # constructors
    # --------------------------------------------------------------------------

    @classmethod
    def from_skeleton_lines(cls, lines=[]):

        network = Network.from_lines(lines)
        sk3_node = cls.from_network(network)

        return sk3_node

    @classmethod
    def from_network(cls, network=None):
        sk3_node = cls()

        sk3_node.network = network
        if len(sk3_node.network_nodes[0]) != 1:
            print('only one joint node is allowed to make a skeleton3d node!')
            return

        sk3_node.get_convexhull_mesh()
        sk3_node.get_descendent_tree()
        sk3_node.add_skeleton_vertices()
        sk3_node.add_skeleton_faces()
        sk3_node.update_vertices_location()

        return sk3_node

    # --------------------------------------------------------------------------
    # constructors
    # --------------------------------------------------------------------------

    def get_convexhull_mesh(self):
        # make a convexhull mesh from all leaf points of network

        network_leafs = self.network_nodes[1]
        points = [self.network.node_coordinates(key) for key in network_leafs]

        self.convexhull_mesh, convexhull_mesh_vertices = \
            get_convex_hull_mesh(points)

        self.network_convexhull = dict(
            zip(network_leafs, convexhull_mesh_vertices)
            )

    def get_descendent_tree(self):
        # copy convexhull mesh halfedge dictionary \
        # as descendent tree to store information

        self.attributes.update({
            'descendent_tree': copy.deepcopy(self.convexhull_mesh.halfedge)
        })

        for u, v in self.convexhull_mesh.edges():
            self.attributes['descendent_tree'][u][v] = {'jp': None, 'lp': None}
            self.attributes['descendent_tree'][v][u] = {'jp': None, 'lp': None}

    def add_skeleton_vertices(self):
        # asign keys to all new vertices
        self._add_joint_vertices()
        self._add_leaf_vertices()

    def _add_joint_vertices(self):
        current_key = self.number_of_vertices()

        for fkey in self.convexhull_mesh.faces():
            face = self.convexhull_mesh.face[fkey]
            vertices = face + [face[0]]
            for u, v in pairwise(vertices):
                self.attributes['descendent_tree'][u][v].update({'jp': current_key})

            self.add_vertex(current_key)
            current_key += 1

    def _add_leaf_vertices(self):
        current_key = self.number_of_vertices()

        for key in self.convexhull_mesh.vertices():
            nbrs = self.convexhull_mesh.vertex_neighbors(key)
            for nbr in nbrs:
                self.attributes['descendent_tree'][key][nbr].update({'lp': current_key})
                self.add_vertex(current_key)

                current_key += 1

    def add_skeleton_faces(self):
        for key in self.convexhull_mesh.vertices():
            nbrs = self.convexhull_mesh.vertex_neighbors(key, ordered=True)
            vertices = nbrs + [nbrs[0]]
            for a, b in pairwise(vertices):
                face = [
                    self.descendent_tree[key][a]['lp'],
                    self.descendent_tree[key][a]['jp'],
                    self.descendent_tree[key][b]['jp'],
                    self.descendent_tree[key][b]['lp']
                ]
                self.add_face(face)

    def update_vertices_location(self):

        pt_center = self.network.node_coordinates(self.network_nodes[0][0])

        # add coordiates to 'jp' of each edge of descendent tree
        for fkey in self.convexhull_mesh.faces():
            face = self.convexhull_mesh.face[fkey]
            vecs_join_to_leaf = [
                Vector.from_start_end(
                    pt_center, self.convexhull_mesh.vertex_coordinates(v)
                    )
                for v in face
                ]

            vecs_join_to_leaf = _vecs_unitize(vecs_join_to_leaf)
            vec_joint_to_face = _equal_angle_vector(vecs_join_to_leaf)

            vec = Vector(*vec_joint_to_face)
            vec.unitize()
            vec.scale(self.joint_width)

            pt = add_vectors(pt_center, vec)

            # v_keys = face + [face[0]]
            # for u, v in pairwise(v_keys):
            #     self.attributes['descendent_tree'][u][v].update({'jp': current_key})

            vertex_key = self.descendent_tree[face[0]][face[1]]['jp']
            self.vertex[vertex_key].update({'x': pt[0], 'y': pt[1], 'z': pt[2]})

        # add coordiates to 'lp' of each edge of descendent tree
        for key in self.convexhull_mesh.vertices():
            pt_leaf = self.convexhull_mesh.vertex_coordinates(key)
            nbrs = self.convexhull_mesh.vertex_neighbors(key)

            for nbr in nbrs:
                pt_joint = self.vertex_coordinates(self.descendent_tree[key][nbr]['jp'])
                vec_edge = Vector.from_start_end(pt_center, pt_leaf)
                pln_end = Plane(pt_leaf, vec_edge)
                pt = project_point_plane(pt_joint, pln_end)
                vec_leaf = Vector.from_start_end(pt_leaf, pt)
                vec_leaf.unitize()
                vec_leaf.scale(self.leaf_width)
                pt = add_vectors(pt_leaf, vec_leaf)

                vertex_key = self.descendent_tree[key][nbr]['lp']
                self.vertex[vertex_key].update({'x': pt[0], 'y': pt[1], 'z': pt[2]})


class Skeleton3D_Branch(Mesh):
    def __init__(self):
        super(Skeleton3D_Branch, self).__init__()
        self.attributes.update({
            'sk3_nodes': None,
        })
