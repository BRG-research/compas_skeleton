from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from compas.datastructures import Mesh
from compas.geometry import Vector
from compas.geometry import normalize_vector
from compas.geometry import add_vectors
from compas.geometry import orient_points
from compas.geometry.hull import convex_hull
from compas.utilities import pairwise

import math

__all__ = ['Skeleton3D']


class Skeleton3D(Mesh):

    def __init__(self):
        super(Skeleton3D, self).__init__()
        self.node = {}
        self.halfbranch = {}
        self.branch_radius = 1.0
        self.section_seg = 4
        self.node_radius_fac = 1.0

    @classmethod
    def from_skeleton_lines(cls, lines=[]):
        from compas.datastructures import Network

        sk3 = cls()
        network = Network.from_lines(lines)

        sk3.node = network.node
        sk3.halfbranch = network.adjacency

        return sk3

    @property
    def nodes_joint(self):
        nodes_joint = []
        for key in self.node:
            if not self.is_node_leaf(key):
                nodes_joint.append(key)

        return nodes_joint

    # --------------------------------------------------------------------------
    # builders
    # --------------------------------------------------------------------------

    def generate_mesh(self):
        self._get_pts_for_branches()
        self._generate_branches_mesh()
        self._generate_nodes_mesh()

    def _generate_nodes_mesh(self):
        for key in self.nodes_joint:
            self._generate_node_mesh(key)

    def _generate_node_mesh(self, u):
        keys = []
        for v in self.halfbranch[u]:
            keys.extend(self.halfbranch[u][v])

        points = [self.vertex_attributes(key, 'xyz') for key in keys]
        faces_index = convex_hull(points)

        for face_index in faces_index:
            face = [keys[i] for i in face_index]
            add_face = True

            for v in self.halfbranch[u]:
                if len(set(face) & set(self.halfbranch[u][v])) == 3:
                    add_face = False
                    break

            if add_face:
                self.add_face(face)

    def _generate_branches_mesh(self):
        for u, v in self.branches():
            self._generate_branch_mesh(u, v)

    def _generate_branch_mesh(self, u, v):
        keys1 = self.halfbranch[u][v]
        keys2 = self.halfbranch[v][u]

        index = list(pairwise(range(len(keys1)))) + [(len(keys1)-1, 0)]
        for i, j in index:
            self.add_face([
                keys1[i], keys1[j], keys2[j], keys2[i]
                ])

    def _get_pts_for_branches(self):
        for u, v in self.branches():
            self._get_pts_for_branch(u, v)

    def _get_pts_for_branch(self, u, v):
        self._get_pts_for_halfbranch(u, v, 1)
        self._get_pts_for_halfbranch(v, u, -1)

    def _get_pts_for_halfbranch(self, u, v, flag):
        pt_u = [self.node[u][xyz] for xyz in 'xyz']
        pt_v = [self.node[v][xyz] for xyz in 'xyz']
        vec = Vector.from_start_end(pt_u, pt_v)
        vec.unitize()

        buffer_dist = self._calculate_nodes_radius() * self.node_radius_fac
        if not self.is_node_leaf(u):
            pt_u = add_vectors(pt_u, vec * buffer_dist)

        target_plane = (pt_u, vec * flag)  # flip vec for the other end
        points = self._generate_section(target_plane)

        keys = [self.add_vertex(x=x, y=y, z=z) for x, y, z in points]
        self.halfbranch[u][v] = keys

    def _generate_section(self, target_plane):
        theta = 2 * math.pi / self.section_seg
        points = [
            (
                self.branch_radius * math.cos(theta * i),
                self.branch_radius * math.sin(theta * i),
                0.
            ) for i in range(self.section_seg)
            ]

        ref_plane = ([0.0, 0.0, 0.0], [0.0, 0.0, 1.0])

        return orient_points(points, ref_plane, target_plane)

    def _calculate_nodes_radius(self):

        node_radius_all = [self._calculate_node_radius(key) for key in self.nodes_joint]
        return max(node_radius_all)

    def _calculate_node_radius(self, key):
        nbrs = list(self.halfbranch[key])

        pt_center = [self.node[key][xyz] for xyz in 'xyz']
        pt_nbrs = [[self.node[nbr][xyz] for xyz in 'xyz'] for nbr in nbrs]

        vecs = [normalize_vector(Vector.from_start_end(pt_center, pt_nbr)) for pt_nbr in pt_nbrs]
        pts = [add_vectors(pt_center, vec) for vec in vecs]

        ang_min = math.pi * 2
        for i, pt1 in enumerate(pts):
            for j, pt2 in enumerate(pts):
                if i == j:
                    continue

                vec1 = Vector.from_start_end(pt_center, pt1)
                vec2 = Vector.from_start_end(pt_center, pt2)
                ang_min = min(ang_min, vec1.angle(vec2))

        return self.branch_radius/math.tan(ang_min * .5)

    # --------------------------------------------------------------------------
    # info
    # --------------------------------------------------------------------------

    def is_node_leaf(self, key):
        return len(list(self.halfbranch[key])) == 1

    def branches(self):
        seen = set()
        for u in self.halfbranch:
            for v in self.halfbranch[u]:
                key = u, v
                ikey = v, u
                if key in seen or ikey in seen:
                    continue
                seen.add(key)
                seen.add(ikey)

                yield key

    # --------------------------------------------------------------------------
    # modifiers
    # --------------------------------------------------------------------------

    def merge_triangles(self):
        faces_to_merge = []
        seen = []
        for u, v in self.edges():
            f1 = self.halfedge[u][v]
            f2 = self.halfedge[v][u]
            if not f1 or not f2:
                continue

            if f1 in seen or f2 in seen:
                continue

            if len(self.face[f1]) == len(self.face[f2]) == 3:
                faces_to_merge.append([f1, f2])
                seen.extend([f1, f2])

        for f1, f2 in faces_to_merge:
            self.merge_triangle(f1, f2)

    def merge_triangle(self, f1, f2):
        face1, face2 = self.face[f1], self.face[f2]
        if len(face1) == len(face2) == 3:
            keys_shared = set(face1) & set(face2)
            if len(keys_shared) == 2:
                u, v = keys_shared
                if (u, v) in self.face_halfedges(f1):
                    add_face = [
                        u,
                        face2[(face2.index(u) + 1) % 3],
                        v,
                        face1[(face1.index(v) + 1) % 3]
                        ]
                else:
                    add_face = [
                        u,
                        face1[(face1.index(u) + 1) % 3],
                        v,
                        face2[(face2.index(v) + 1) % 3]
                        ]

                self.delete_face(f1)
                self.delete_face(f2)

                self.add_face(add_face)


if __name__ == '__main__':
    pass
