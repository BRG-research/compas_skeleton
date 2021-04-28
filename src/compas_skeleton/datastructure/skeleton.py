from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from compas.datastructures import Mesh
from compas.datastructures import mesh_subdivide_catmullclark
from compas.datastructures import Network
from compas.datastructures.network import duality

from compas.geometry import centroid_points
from compas.geometry import Vector
from compas.geometry import add_vectors
from compas.geometry import Frame

import copy

__all__ = ['Skeleton']


class Skeleton(Mesh):
    """Skeleton is a mesh topologically generated from a set of lines with special attributes.

    Attributes
    ----------
    node_width : float
        mesh width at all skeleton joints
    leaf_width : float
        mesh width at all skeleton leaf ends
    leaf_extend : float
        distance value of how far the leaf vertices extend
    sub_level : int
        subdivision level of high-poly mesh

    Examples
    --------
    >>> from compas_skeleton.datastructure import Skeleton
    >>> lines = [
    >>> ([0.0, 0.0, 0.0], [0.0, 10.0, 0.0]),
    >>> ([0.0, 0.0, 0.0], [-8.6, -5.0, 0.0]),
    >>> ([0.0, 0.0, 0.0], [8.6, -5.0, 0.0])
    >>> ]
    >>> skeleton = Skeleton.from_skeleton_lines(lines)
    """

    def __init__(self):
        super(Skeleton, self).__init__()
        self.attributes.update({
            'name': 'Skeleton',
            'leaf_width': 0,
            'node_width': 0,
            'leaf_extend': 0,
            'sub_level': 0
        })
        self.update_default_vertex_attributes({'type': None})
        self.update_default_vertex_attributes({'transform': [0, 0, 0]})
        self.update_default_edge_attributes({'type': None})

    # --------------------------------------------------------------------------
    # special attributes
    # --------------------------------------------------------------------------

    @property
    def leaf_width(self):
        return self.attributes['leaf_width']

    @leaf_width.setter
    def leaf_width(self, dist):
        self.attributes['leaf_width'] = dist

    @property
    def node_width(self):
        return self.attributes['node_width']

    @node_width.setter
    def node_width(self, dist):
        self.attributes['node_width'] = dist

    @property
    def leaf_extend(self):
        return self.attributes['leaf_extend']

    @leaf_extend.setter
    def leaf_extend(self, dist):
        self.attributes['leaf_extend'] = dist

    @property
    def skeleton_vertices(self):
        """ get skeleton vertices keys.
        Return
        ------
        vertex keys: two lists of int
            keys of skeleton joint vertices and skeleton leaf vertices

        Example
        -------
        skeleton = Skeleton.from_lines(lines)
        joint_keys, leaf_keys = skeleton.skeleton_vertices

        """
        skeleton_nodes = list(self.vertices_where({'type': 'skeleton_node'}))
        skeleton_leaves = list(self.vertices_where({'type': 'skeleton_leaf'}))

        return skeleton_nodes, skeleton_leaves

    @property
    def skeleton_branches(self):
        """ get skeleton branches keys.
        Return
        ------
        edge keys: list of tuples
            keys of edges which are skeleton branches(identical with input lines)

        Example
        -------
        skeleton = Skeleton.from_lines(lines)
        print(skeleton.skeleton_branches)

        """
        return list(self.edges_where({'type': 'skeleton_branch'}))

    # --------------------------------------------------------------------------
    # constructors
    # --------------------------------------------------------------------------

    @classmethod
    def from_skeleton_lines(cls, lines=[]):
        """ Instantiate a skeleton from lines.

        Parameters
        ----------
        lines: :class:`compas.geometry.Line`
            a list of compas lines

        Return
        ------
        skeleton: :class:`compas_skeleton.datastructure.Skeleton`
            a skeleton object

        Examples
        --------
        >>> lines = [
        >>> ([0.0, 0.0, 0.0], [0.0, 10.0, 0.0]),
        >>> ([0.0, 0.0, 0.0], [-8.6, -5.0, 0.0]),
        >>> ([0.0, 0.0, 0.0], [8.6, -5.0, 0.0])
        >>> ]
        >>> skeleton = Skeleton.from_skeleton_lines(lines)
        """

        skeleton = cls()

        network = Network.from_lines(lines)
        skeleton._mesh_from_network(network)

        return skeleton

    @classmethod
    def from_center_point(cls, point=None):
        """ Instantiate a skeleton from a single point.

        Parameters
        ----------
        point: :class:`compas.geometry.Point`
            a tuple of 3 coordinates

        Return
        -------
        skeleton: :class:`compas_skeleton.datastructure.Skeleton`
            a skeleton object

        Examples
        --------
        >>> point = [0, 0, 0]
        >>> skeleton = Skeleton.from_center_point(point)
        """

        skeleton = cls()
        skeleton._mesh_from_center_point(point)

        return skeleton

    def update_skeleton_lines(self, lines=[]):
        """ Update skeleton by adding more skeleon lines or remove current skeleton lines.

        Parameters
        ----------
        lines: :class:`compas.geometry.Line`
            a list of compas lines.

        Examples
        --------
        >>> lines = [
        >>> ([0.0, 0.0, 0.0], [0.0, 10.0, 0.0]),
        >>> ([0.0, 0.0, 0.0], [-8.6, -5.0, 0.0]),
        >>> ([0.0, 0.0, 0.0], [8.6, -5.0, 0.0])
        >>> ]
        >>> skeleton = Skeleton.from_skeleton_lines(lines)
        >>>
        >>> lines.append(([0.0, 10.0, 0.0], [5.0, 10.0, 0.0]))
        >>> skeleton = Skeleton.update_skeleton_lines(lines)
        """
        network = Network.from_lines(lines)

        self.clear()
        self._mesh_from_network(network)

    # --------------------------------------------------------------------------
    # builders
    # --------------------------------------------------------------------------

    def _mesh_from_network(self, network):
        # input from network
        self._add_skeleton_vertices(network)
        self._add_skeleton_branches(network)

        # assign default mesh width, because with 0 width the mesh cannot be visualised.
        if self.node_width == 0 and self.leaf_width == 0:
            average_edge_length = sum(
                [self.edge_length(u, v) for u, v in self.edges()])/self.number_of_edges()
            self.leaf_width = average_edge_length * 0.2
            self.node_width = average_edge_length * 0.2 * 2

        # add generated vertices keys and faces
        network = self._add_boundary_vertices(network)
        self._add_mesh_faces(network)

        # update vertices positions accoding to current node width, leaf width
        self.update_mesh_vertices_pos()

    def _mesh_from_center_point(self, pt):
        # add the point as the skeleton node
        self.add_vertex(0)
        self.vertex[0].update(
            {'x': pt[0], 'y': pt[1], 'z': pt[2], 'type': 'skeleton_node'})

        # add 4 more vertices to compose a mesh
        for index in range(1, 5):
            self.add_vertex(index)

        from compas.utilities import pairwise

        keys = list(range(1, 5) + [1])
        for u, v in pairwise(keys):
            self.add_face([0, u, v])

        if self.node_width == 0:
            self.node_width = 2  # for default display.

        self.update_mesh_vertices_pos()

    def _add_skeleton_vertices(self, network):
        duality.network_sort_neighbors(network, True)

        for key in network.nodes():
            if network.is_leaf(key):
                network.node[key].update({'type': 'skeleton_leaf'})
            else:
                network.node[key].update({'type': 'skeleton_node'})

            self.add_vertex(key)
            self.vertex[key].update(network.node[key])

    def _add_skeleton_branches(self, network):
        self.halfedge = copy.deepcopy(network.adjacency)
        for key, attr in self.edges(True):
            attr.update({'type': 'skeleton_branch'})

    def _add_boundary_vertices(self, network):
        """ Assgin two new keys to each network halfedge so a face can be added to skeleton.
        Note:
        -----
        for each skeleton node vertex, iterate all halfedges which start form it.
        assign a new vertex key to each of the halfedge,
        store it as the 'sp' for this halfedge[u][v],
        store it as the 'ep' for the adjacent halfedge[prvs, u].

        for each skeleton leaf vertex, assign two new vertex keys.
        store it as 'sp' for haledge[u][v] whitch starts from this leaf vertex,
        store another one as 'ep' for [v][u] which ends to it.

        after all iterations, each halfedge will have a 'sp' and an 'ep'. A face = [u, v, 'ep', 'sp'] could be added to skeleton.
        """
        def get_boundary_vertex_keys(network, u, v, sp=None, ep=None):
            attr = network.adjacency[u][v]
            if not attr:
                attr = {}
            if sp:
                attr['sp'] = sp
            if ep:
                attr['ep'] = ep
            network.adjacency[u][v] = attr

        current_key = network.number_of_nodes()
        node_vertices, leaf_vertices = self.skeleton_vertices

        for u in node_vertices:
            for v in network.adjacency[u]:

                vertex_prvs = self._find_previous_vertex(u, v)
                get_boundary_vertex_keys(network, u, v, sp=current_key)
                get_boundary_vertex_keys(
                    network, vertex_prvs, u, ep=current_key)

                self.add_vertex(current_key)
                current_key += 1

        for u in leaf_vertices:
            v = list(network.adjacency[u].items())[0][0]

            get_boundary_vertex_keys(network, u, v, sp=current_key)
            get_boundary_vertex_keys(network, v, u, ep=current_key+1)

            self.add_vertex(current_key)
            self.add_vertex(current_key+1)
            current_key += 2

        return network

    def _add_mesh_faces(self, network):
        for u in network.adjacency:
            for v in network.adjacency[u]:
                self.add_face([
                    u, v,
                    network.adjacency[u][v]['ep'],
                    network.adjacency[u][v]['sp']
                ])

    # --------------------------------------------------------------------------
    # modifiers
    # --------------------------------------------------------------------------

    def update_mesh_vertices_pos(self):
        """Update all the vertex coordiates.

        Examples
        --------
        >>> skeleton.node_width = 20
        >>> skeleton.update_mesh_vertices_pos()
        """

        def update_node_boundary_vertex(u, v):
            fkey = self.halfedge[u][v]
            key = self.face[fkey][3]
            pt = self._get_node_boundary_vertex_pos(u, v)
            vec = Vector(*self.vertex_attribute(key, 'transform'))
            pt = add_vectors(pt, vec)

            self.vertex[key].update({'x': pt[0], 'y': pt[1], 'z': pt[2]})

        def update_leaf_boundary_vertex(u, v):
            fkey1 = self.halfedge[u][v]
            fkey2 = self.halfedge[v][u]
            key1 = self.face[fkey1][3]
            key2 = self.face[fkey2][2]

            pt1, pt2 = self._get_leaf_boundary_vertex_pos(u, v)
            vec1 = Vector(*self.vertex_attribute(key1, 'transform'))
            vec2 = Vector(*self.vertex_attribute(key2, 'transform'))
            pt1 = add_vectors(pt1, vec1)
            pt2 = add_vectors(pt2, vec2)

            self.vertex[key1].update({'x': pt1[0], 'y': pt1[1], 'z': pt1[2]})
            self.vertex[key2].update({'x': pt2[0], 'y': pt2[1], 'z': pt2[2]})

        def update_dome_boundary_vertex():
            pts = self._get_dome_boundary_vertex_pos()

            for key in range(1, 5):
                pt = pts[key-1]
                vec = Vector(*self.vertex_attribute(key, 'transform'))
                pt = add_vectors(pt, vec)
                self.vertex[key].update({'x': pt[0], 'y': pt[1], 'z': pt[2]})

        if list(self.skeleton_branches):
            for u, v in self.skeleton_branches:
                if self.vertex[u]['type'] == 'skeleton_node':
                    update_node_boundary_vertex(u, v)
                else:
                    update_leaf_boundary_vertex(u, v)
                if self.vertex[v]['type'] == 'skeleton_node':
                    update_node_boundary_vertex(v, u)
                else:
                    update_leaf_boundary_vertex(v, u)

        else:
            update_dome_boundary_vertex()

    def _update_width(self, dist, flag):

        if flag == 'leaf_width':
            self.leaf_width = dist
        elif flag == 'node_width':
            self.node_width = dist
        elif flag == 'leaf_extend':
            self.leaf_extend = dist

    def _get_node_boundary_vertex_pos(self, u, v):

        vec_offset = self._get_vec_offsetfrom_branch(u, v, 'left')
        vec_offset.scale(self.node_width)
        pt_node = add_vectors(self.vertex_coordinates(u), vec_offset)

        return pt_node

    def _get_leaf_boundary_vertex_pos(self, u, v):
        vec_along_edge = Vector(*self.edge_vector(v, u))
        vec_offset = vec_along_edge.cross(Vector.Zaxis())
        if vec_offset.length < 0.001:
            raise Exception(
                'skeleton line shouldn\'t be perpendicular to the ground')

        vec_offset.unitize()
        vec_offset.scale(self.leaf_width)

        pt_leaf = self.vertex_coordinates(u)
        pt_leaf_right = add_vectors(pt_leaf, vec_offset)
        pt_leaf_left = add_vectors(pt_leaf, vec_offset.scaled(-1))

        vec_extend = vec_along_edge.unitized() * self.leaf_extend
        pt_leaf_right = add_vectors(pt_leaf_right, vec_extend)
        pt_leaf_left = add_vectors(pt_leaf_left, vec_extend)

        return pt_leaf_right, pt_leaf_left

    def _get_dome_boundary_vertex_pos(self):
        from compas.geometry import Frame

        vec_x = Frame.worldXY().xaxis
        vec_y = Frame.worldXY().yaxis

        vec_x.scale(self.attributes['node_width'])
        vec_y.scale(self.attributes['node_width'])

        pts = [
            add_vectors(self.vertex_coordinates(0), vec_x),
            add_vectors(self.vertex_coordinates(0), vec_y),
            add_vectors(self.vertex_coordinates(0), vec_x * -1),
            add_vectors(self.vertex_coordinates(0), vec_y * -1)
        ]

        return pts

    def _get_vec_along_branch(self, v):
        u = self.vertex_attribute(v, 'neighbors')[0]

        return Vector(*(self.edge_vector(u, v)))

    def _get_vec_offsetfrom_branch(self, u, v, dirct):
        if dirct == 'left':
            vertex = self._find_previous_vertex(u, v)
        else:
            vertex = self._find_next_vertex(u, v)

        vec1 = Vector(*self.edge_vector(u, v))
        vec2 = Vector(*self.edge_vector(vertex, u))
        normal = vec1.cross(vec2)

        if normal.length < 0.001:  # if the two adjacent edges are parallel
            vec_offset = Vector.Zaxis().cross(vec1)
        else:
            pt_face_center = centroid_points([
                self.vertex_coordinates(vertex),
                self.vertex_coordinates(u),
                self.vertex_coordinates(v)
            ])
            vec_offset = Vector.from_start_end(
                self.vertex_coordinates(u), pt_face_center)
            # if the angle between two vectors is bigger than 180, the offset direction should be flipped.
            vec_offset.scale(normal[2] * -1)

        vec_offset.unitize()
        if dirct == 'right':
            vec_offset.scale(-1)

        return vec_offset

    def _get_leaf_vertex_frame(self, key):
        pt = self.vertex_coordinates(key)
        vec_along_edge = self._get_vec_along_branch(key)
        vec_perp = vec_along_edge.cross(Vector.Zaxis())

        return Frame(pt, vec_along_edge, vec_perp)

    def _get_joint_vertex_frame(self, u, v):
        pt = self.vertex_coordinates(u)

        vec_offsetfrom_edge = self._get_vec_offsetfrom_branch(u, v, 'left')
        vec_perp = vec_offsetfrom_edge.cross(Vector.Zaxis())
        frame_left = Frame(pt, vec_offsetfrom_edge, vec_perp)

        vec_offsetfrom_edge = self._get_vec_offsetfrom_branch(u, v, 'right')
        vec_perp = vec_offsetfrom_edge.cross(Vector.Zaxis())
        frame_right = Frame(pt, vec_offsetfrom_edge, vec_perp)

        return frame_left, frame_right

    def _get_centerpt_frame(self, key):
        pt = self.vertex_coordinates(key)
        return Frame(pt, Frame.worldXY().xaxis, Frame.worldXY().yaxis)

    def _mount_leaf_transformation(self, v, f1, f2):
        #  mount the transformation of skeleton vertice to related mesh vertices
        u = self.vertex_attribute(v, 'neighbors')[0]
        descendents = self._get_descendent(u, v)[:2]

        for key in descendents:
            self._mount_skeleton_vertex_transformation(key, f1, f2)

    def _mount_joint_transformation(self, u, v, f1, f2, dirct):

        if dirct == 'left':
            key = self._get_descendent(u, v)[2]
        else:
            key = self._get_descendent(u, v)[3]

        self._mount_skeleton_vertex_transformation(key, f1, f2)

    def _mount_skeleton_vertex_transformation(self, key, f1, f2):
        # mount the skeleton vertex transformation to a descendent mesh vertex transformation
        vec = Vector(*self.vertex_attribute(key, 'transform'))
        vec_l = f1.to_local_coordinates(vec)
        vec = f2.to_world_coordinates(vec_l)
        self.vertex[key].update({'transform': list(vec)})

    def _find_previous_vertex(self, u, v):
        """ Find the previous vertex of a halfedge[u][v] through sorted nbrs. """
        nbrs = self.vertex[u]['neighbors']
        prvs = nbrs[(nbrs.index(v) + 1) % len(nbrs)]
        return prvs

    def _find_next_vertex(self, u, v):
        """ Find the next vertex of a halfedge[u][v] through sorted nbrs. """
        nbrs = self.vertex[u]['neighbors']
        next = nbrs[(nbrs.index(v) - 1) % len(nbrs)]
        return next

    def _get_descendent(self, u, v):
        fkey1 = self.halfedge[u][v]
        fkey2 = self.halfedge[v][u]

        leaf_left = self.face[fkey1][2]
        joint_left = self.face[fkey1][3]
        leaf_right = self.face[fkey2][3]
        joint_right = self.face[fkey2][2]

        return leaf_left, leaf_right, joint_left, joint_right

    # --------------------------------------------------------------------------
    # visualization
    # --------------------------------------------------------------------------

    def subdivide(self, k=1):
        """Increase the catmull-clark subdivison level of high-poly mesh

        Examples
        --------
        >>> skeleton.subdivide(2)
        """
        self.attributes['sub_level'] += k

    def merge(self, k=1):
        """Decrease the catmull-clark subdivison level of high-poly mesh

        Examples
        --------
        >>> skeleton.merge(1)
        """
        if self.attributes['sub_level'] > 0:
            self.attributes['sub_level'] -= k

    def _subdivide(self, k=1):
        corners = []
        for key in self.vertices():
            if self.vertex_degree(key) == 2:
                corners.append(key)

        self.default_edge_attributes.update({'crease': 0})
        self.edges_attribute(
            'crease', k + 1, keys=[edge for boundary in self.edges_on_boundaries() for edge in boundary])

        return mesh_subdivide_catmullclark(self, k, fixed=corners)

    # --------------------------------------------------------------------------
    # exporting
    # --------------------------------------------------------------------------

    def to_mesh(self):
        """Return the high-poly skeleton mesh as a compas mesh

        Return
        ------
        mesh: :class:`compas.datastructures.Mesh`
        """
        mesh = Mesh()
        highpoly_mesh = self._subdivide(self.attributes['sub_level'])

        for key, attr in highpoly_mesh.vertices(True):
            mesh.add_vertex(key, x=attr['x'], y=attr['y'], z=attr['z'])

        for fkey in highpoly_mesh.face:
            mesh.add_face(highpoly_mesh.face[fkey])

        mesh.name = 'Skeleton'
        return mesh


if __name__ == '__main__':
    pass
