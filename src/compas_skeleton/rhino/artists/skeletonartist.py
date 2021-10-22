from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from functools import partial

import compas_rhino
from compas_rhino.artists import BaseArtist

from compas.utilities import color_to_colordict
from compas.geometry import centroid_polygon
from compas.utilities import pairwise


colordict = partial(color_to_colordict, colorformat='rgb', normalize=False)


__all__ = ["SkeletonArtist"]


class SkeletonArtist(BaseArtist):
    """Artist for the visualisation of Skeleton data structures."""

    def __init__(self, skeleton, layer=None):
        super(SkeletonArtist, self).__init__()
        self._skeleton = None
        self._subd = None
        self._vertex_xyz = None
        self._subd_vertex_xyz = None
        self.skeleton = skeleton
        self.subd = skeleton.to_mesh()
        self.layer = layer
        self.color_vertices = (255, 0, 0)
        self.color_edges = (0, 0, 255)
        self.color_mesh_vertices = (0, 0, 0)
        self.color_mesh_edges = (0, 0, 0)

    @property
    def skeleton(self):
        return self._skeleton

    @skeleton.setter
    def skeleton(self, skeleton):
        self._skeleton = skeleton
        self._vertex_xyz = None

    @property
    def subd(self):
        return self._subd

    @subd.setter
    def subd(self, subd):
        self._subd = subd
        self._subd_vertex_xyz = None

    @property
    def vertex_xyz(self):
        if not self._vertex_xyz:
            self._vertex_xyz = {vertex: self.skeleton.vertex_attributes(vertex, 'xyz') for vertex in self.skeleton.vertices()}
        return self._vertex_xyz

    @vertex_xyz.setter
    def vertex_xyz(self, vertex_xyz):
        self._vertex_xyz = vertex_xyz

    @property
    def subd_vertex_xyz(self):
        if not self._subd_vertex_xyz:
            self._subd_vertex_xyz = {vertex: self.subd.vertex_attributes(vertex, 'xyz') for vertex in self.subd.vertices()}
        return self._subd_vertex_xyz

    @subd_vertex_xyz.setter
    def subd_vertex_xyz(self, subd_vertex_xyz):
        self._subd_vertex_xyz = subd_vertex_xyz

    # ==========================================================================
    # clear
    # ==========================================================================

    def clear_by_name(self):
        """Clear all objects in the "namespace" of the associated skeleton."""
        guids = compas_rhino.get_objects(name="{}.*".format(self.skeleton.name))
        compas_rhino.delete_objects(guids, purge=True)

    def clear_layer(self):
        """Clear the main layer of the artist."""
        if self.layer:
            compas_rhino.clear_layer(self.layer)

    # ==========================================================================
    # draw
    # ==========================================================================

    def draw(self):
        """Draw the skeleton vertices and branches and the resulting (dense) mesh."""
        pass

    # ==========================================================================
    # The skeleton
    # ==========================================================================

    def draw_skeleton_vertices(self, vertices=None, color=None):
        """Draw the skeleton vertices."""
        vertices = vertices or list(self.skeleton.skeleton_vertices[0] + self.skeleton.skeleton_vertices[1])
        vertex_xyz = self.vertex_xyz
        vertex_color = colordict(color, vertices, default=self.color_vertices)
        points = []
        for vertex in vertices:
            points.append({
                'pos': vertex_xyz[vertex],
                'name': "{}.vertex.{}".format(self.skeleton.name, vertex),
                'color': vertex_color[vertex]})
        return compas_rhino.draw_points(points, layer=self.layer, clear=False, redraw=True)

    def draw_skeleton_edges(self, edges=None, color=None):
        """Draw the skeleton edges."""
        edges = edges or list(self.skeleton.skeleton_branches)
        vertex_xyz = self.vertex_xyz
        edge_color = colordict(color, edges, default=self.color_edges)
        lines = []
        for edge in edges:
            lines.append({
                'start': vertex_xyz[edge[0]],
                'end': vertex_xyz[edge[1]],
                'color': edge_color[edge],
                'name': "{}.edge.{}-{}".format(self.skeleton.name, *edge)})
        return compas_rhino.draw_lines(lines, layer=self.layer, clear=False, redraw=True)

    # ==========================================================================
    # The coarse mesh
    # ==========================================================================

    def draw_mesh_vertices(self, vertices=None, color=None):
        """Draw the vertices of the coarse mesh."""
        mesh_vertices = set(self.skeleton.vertices())
        skeleton_vertices = set(self.skeleton.skeleton_vertices[0] + self.skeleton.skeleton_vertices[1])
        vertex_xyz = self.vertex_xyz
        vertices = vertices or list(mesh_vertices - skeleton_vertices)
        vertex_color = colordict(color, vertices, default=self.color_mesh_vertices)
        points = []
        for vertex in vertices:
            points.append({
                'pos': vertex_xyz[vertex],
                'name': "{}.vertex.{}".format(self.skeleton.name, vertex),
                'color': vertex_color[vertex]})
        return compas_rhino.draw_points(points, layer=self.layer, clear=False, redraw=True)

    def draw_mesh_edges(self, edges=None, color=None):
        """Draw the edges of the coarse mesh."""
        pass

    # ==========================================================================
    # The subd mesh
    # ==========================================================================

    def draw_subd(self, color=(0, 0, 0)):

        subd_vertex_index = self.subd.key_index()
        subd_vertex_xyz = self.subd_vertex_xyz
        vertices = [subd_vertex_xyz[vertex] for vertex in self.subd.vertices()]
        faces = [[subd_vertex_index[vertex] for vertex in self.subd.face_vertices(face)] for face in self.subd.faces()]
        new_faces = []
        for face in faces:
            f = len(face)
            if f == 3:
                new_faces.append(face + face[-1:])
            elif f == 4:
                new_faces.append(face)
            elif f > 4:
                centroid = len(vertices)
                vertices.append(centroid_polygon([vertices[index] for index in face]))
                for a, b in pairwise(face + face[0:1]):
                    new_faces.append([centroid, a, b, b])
            else:
                continue
        layer = self.layer
        name = "{}".format(self.subd.name)
        guid = compas_rhino.draw_mesh(vertices, new_faces, layer=layer, name=name, color=color, disjoint=False)
        return [guid]
