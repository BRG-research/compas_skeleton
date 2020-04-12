from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from compas.geometry import Vector
from compas.geometry import dot_vectors
from compas.geometry import add_vectors
from compas.geometry import Frame
import compas_rhino
from compas_rhino.modifiers import mesh_move_vertex
from compas_rhino import delete_objects
from compas_skeleton.rhino import SkeletonArtist

import Rhino
from Rhino.Geometry import Point3d
from Rhino.Geometry import Line
from System.Drawing.Color import FromArgb
import rhinoscriptsyntax as rs


__all__ = ["SkeletonObject"]


class SkeletonObject(object):
    """Scene object for Skeleton in Rhino.

    Parameters
    ----------
    datastructure : :class:`compas_skeleton.datastructures.Skeleton`
        The Skeleton data structure.

    Attributes
    ----------
    artist : :class:`compas_skeleton.rhino.SkeletonArtist`
        The specialised skeleton object artist.

    Examples
    --------
    >>> from compas_skeleton.datastructure import Skeleton
    >>> from compas_skeleton.rhino import SkeletonObject
    >>> import compas_rhino

    >>> guids = compas_rhino.select_lines()
    >>> lines = compas_rhino.get_line_coordinates(guids)
    >>> skeleton = Skeleton.from_skeleton_lines(lines)
    >>> skeletonobject = SkeletonObject(skeleton)
    >>> skeletonobject.draw()
    >>> skeletonobject.dynamic_update_mesh()
    >>> skeletonobject.update()
    """
    
    settings = {
        'skeleton.layer': "Skeleton::skeleton",
        'mesh.layer': "Skeleton::mesh",
        'color.skeleton.vertices': [255, 0, 0],
        'color.skeleton.edges': [0, 0, 255],
        'color.mesh.vertices': [0, 0, 0],
        'color.mesh.edges': [0, 0, 0],
        'color.mesh.faces': [0, 0, 0]
    }

    def __init__(self, skeleton):
        self.datastructure = skeleton
        self.artist = SkeletonArtist(self.datastructure)
        self.artist.settings.update(self.settings)
        self._guid_skeleton_vertices = {}
        self._guid_skeleton_edges = {}
        self._guid_coarse_mesh_vertices = {}
        self._guid_mesh = {}

    @property
    def guid_skeleton_vertices(self):
        return self._guid_skeleton_vertices

    @guid_skeleton_vertices.setter
    def guid_skeleton_vertices(self, values):
        self._guid_skeleton_vertices = dict(values)
    
    @property
    def guid_skeleton_edges(self):
        return self._guid_skeleton_edges

    @guid_skeleton_edges.setter
    def guid_skeleton_edges(self, values):
        self._guid_skeleton_edges = dict(values)
    
    @property
    def guid_coarse_mesh_vertices(self):
        return self._guid_coarse_mesh_vertices

    @guid_coarse_mesh_vertices.setter
    def guid_coarse_mesh_vertices(self, values):
        self._guid_coarse_mesh_vertices = dict(values)
    
    @property
    def guid_mesh(self):
        return self._guid_mesh

    @guid_mesh.setter
    def guid_mesh(self, values):
        self._guid_mesh = dict(values)

    # ==============================================================================
    # modify datastructure with rhino input
    # ==============================================================================
    
    def add_lines(self):
        """Update skeleton by adding more skeleon lines from Rhino."""
        self.clear_mesh()
        guids = compas_rhino.select_lines()
        if not guids:
            return
        
        guids = list(self.guid_skeleton_edges.keys()) + guids
        lines = compas_rhino.get_line_coordinates(guids)
        compas_rhino.rs.HideObjects(guids)
        self.datastructure.update_skeleton_lines(lines)

    def remove_lines(self):
        """Update skeleton by removing current skeleon lines."""
        self.clear_mesh()
        def custom_filter(rhino_object, geometry, component_index):
            if rhino_object.Attributes.ObjectId in list(self.guid_skeleton_edges.keys()):
                return True
            return False

        guids = rs.GetObjects('select skeleton lines to remove', custom_filter=custom_filter)
        for guid in guids:
            del self.guid_skeleton_edges[guid]
        compas_rhino.rs.DeleteObjects(guids)
        
        lines = compas_rhino.get_line_coordinates(list(self.guid_skeleton_edges.keys()))
        self.datastructure.update_skeleton_lines(lines)

    def dynamic_update_mesh(self):
        """Dynamic update leaf width, node width, leaf extend and draw the mesh in rhino."""
        if self.datastructure.skeleton_vertices()[1]:
            self.dynamic_update_width('leaf_width')

        self.dynamic_update_width('node_width')

        if self.datastructure.skeleton_vertices()[1]:
            self.dynamic_update_width('leaf_extend')

    def dynamic_update_width(self, param):
        """Dynamic update param following mouse movement, and draw the mesh in rhino.
        Parameters
        -----------
        param: str: 'node_width', 'leaf_width', 'leaf_extend'
        """

        # get start point
        gp = Rhino.Input.Custom.GetPoint()
        if param == 'node_width':
            node_vertex = self.datastructure.skeleton_vertices()[0][0]
            sp = Point3d(*(self.datastructure.vertex_coordinates(node_vertex)))
            gp.SetCommandPrompt('select the node vertex')
        else:
            leaf_vertex = self.datastructure.skeleton_vertices()[1][0]
            sp = Point3d(*(self.datastructure.vertex_coordinates(leaf_vertex)))
            gp.SetCommandPrompt('select the leaf vertex')

        gp.SetBasePoint(sp, False)
        gp.ConstrainDistanceFromBasePoint(0.01)
        gp.Get()
        sp = gp.Point()
        gp.SetCommandPrompt('confirm the distance')
        self.clear_mesh()

        # get current point
        def OnDynamicDraw(sender, e):
            cp = e.CurrentPoint
            e.Display.DrawDottedLine(sp, cp, FromArgb(0, 0, 0))

            mp = Point3d.Add(sp, cp)
            mp = Point3d.Divide(mp, 2)
            dist = cp.DistanceTo(sp)
            e.Display.Draw2dText(str(dist), FromArgb(0, 0, 0), mp, False, 20)

            if param == 'leaf_extend':
                direction = _get_leaf_extend_direction(cp)
                dist *= direction

            self.datastructure.update_width(dist, param)
            self.datastructure.update_mesh_vertices_pos()
            lines = _get_edge_lines_in_rhino()

            for line in lines:
                e.Display.DrawLine(line, FromArgb(0, 0, 0), 2)
        
        def _get_constrain(param):
            u = leaf_vertex
            vec_along_edge = self.datastructure._get_vec_along_branch(u)
            
            if param == 'leaf_width':                
                vec_offset = vec_along_edge.cross(Vector.Zaxis())
                vec_rhino = Rhino.Geometry.Vector3d(vec_offset[0], vec_offset[1], vec_offset[2])
            
            if param == 'leaf_extend':
                vec_rhino = Rhino.Geometry.Vector3d(vec_along_edge[0], vec_along_edge[1], vec_along_edge[2])

            pt_leaf = Point3d(*(self.datastructure.vertex_coordinates(u)))
            line = Line(pt_leaf, vec_rhino)
            return line

        def _get_leaf_extend_direction(cp):
            u = leaf_vertex
            vec_along_edge = self.datastructure._get_vec_along_branch(u)
            vec_sp_np = Vector.from_start_end(sp, cp)
            dot_vec = dot_vectors(vec_along_edge, vec_sp_np)
            
            if dot_vec == 0:
                return 0

            return dot_vec / abs(dot_vec)

        def _get_edge_lines_in_rhino():
            sub_mesh = self.datastructure.to_mesh()
            edge_lines = []
            for u, v in sub_mesh.edges():
                pts = sub_mesh.edge_coordinates(u, v)
                line = Line(Point3d(*pts[0]), Point3d(*pts[1]))
                edge_lines.append(line)

            return edge_lines

        if param == 'leaf_width' or param == 'leaf_extend':           
            gp.Constrain(_get_constrain(param))        
        gp.DynamicDraw += OnDynamicDraw

        # get end point
        gp.Get()
        ep = gp.Point()
        dist = ep.DistanceTo(sp)

        if param == 'leaf_extend':
            direction = _get_leaf_extend_direction(ep)
            dist *= direction

        self.datastructure.update_width(dist, param)
        self.datastructure.update_mesh_vertices_pos()

        self.draw_mesh()

    def move_skeleton_vertex(self):
        """ Change the position of a skeleton vertex and update all vertices affected by it. """
        guid = compas_rhino.rs.GetObject(message="Select a vertex.", preselect=True, filter=rs.filter.point | rs.filter.textdot)
        if guid in list(self.guid_skeleton_vertices.keys()):
            key = self.guid_skeleton_vertices[guid]
            f1 = self.datastructure._get_leaf_vertex_frame(key)

            mesh_move_vertex(self.datastructure, key)
            f2 = self.datastructure._get_leaf_vertex_frame(key)
            self.datastructure.update_mesh_vertices_pos(f2, f1)
        
        else:
            print('Not a skeleton vertex! Please select again:')
            return

    def move_mesh_vertex(self):
        """ Update the position of a mesh vertex. """
        guid = compas_rhino.rs.GetObject(message="Select a vertex.", preselect=True, filter=rs.filter.point | rs.filter.textdot)
        guid_key = self.guid_coarse_mesh_vertices
        guid_key.update(self.guid_skeleton_vertices)
        
        key = guid_key[guid]
        sp = self.datastructure.vertex_coordinates(key)
        mesh_move_vertex(self.datastructure, key)
        ep = self.datastructure.vertex_coordinates(key)

        vec = Vector.from_start_end(sp, ep)
        vec_prvs = self.datastructure.vertex_attribute(key, 'transform')
        vec = add_vectors(vec_prvs, vec)
        self.datastructure.vertex[key].update({'transform': list(vec)})

    def update(self):
        """update skeleton and skeleton mesh by typing command name in rhino command line.
            
        Available Commands:
        -------------------
            'm_skeleton'
            'm_mesh'
            'leaf_width'
            'node_width'
            'leaf_extend'
            'subdivide'
            'merge'
            'add_lines'
            'remove_lines'
            'finish'
        """
        while True:            
            operation = compas_rhino.rs.GetString('next')
            if operation == 'm_skeleton':
                self.move_skeleton_vertex()
            elif operation == 'm_mesh':
                self.draw_coarse_mesh_vertices()
                self.move_mesh_vertex()
                self.clear_coarse_mesh_vertices()
            elif operation == 'leaf_width':
                if self.datastructure.skeleton_vertices()[1]:
                    self.dynamic_update_width('leaf_width')
                else:
                    print('this skeleton doesn\'t have any leaf!')
            elif operation == 'node_width':
                self.dynamic_update_width('node_width')
            elif operation == 'leaf_extend':
                self.dynamic_update_width('leaf_extend')
            elif operation == 'subdivide':
                self.datastructure.subdivide(k=1)
            elif operation == 'merge':
                self.datastructure.merge(k=1)
            elif operation == 'add_lines':
                self.add_lines()
            elif operation == 'remove_lines':
                self.remove_lines()

            elif operation == 'finish':
                self.draw()
                break
            else:
                self.draw()
                break

            self.draw()

    # ==============================================================================
    # Visualize
    # ==============================================================================

    def clear(self):
        """ Clear the skeleton and skeleton mesh visualisations in Rhino. """
        self.clear_skeleton()
        self.clear_coarse_mesh_vertices()
        self.clear_mesh()

    def clear_skeleton(self):
        guid_skeleton_vertices = list(self.guid_skeleton_vertices.keys())
        guid_skeleton_edges = list(self.guid_skeleton_edges.keys())
        delete_objects(guid_skeleton_vertices + guid_skeleton_edges, purge=True)
        self._guid_skeleton_vertices = {}
        self._guid_skeleton_edges = {}

    def clear_coarse_mesh_vertices(self):
        guid_coarse_mesh_vertices = list(self.guid_coarse_mesh_vertices.keys())
        delete_objects(guid_coarse_mesh_vertices, purge=True)
        self._coarse_mesh_vertices = {}

    def clear_mesh(self):
        guid_mesh = list(self.guid_mesh.keys())
        delete_objects(guid_mesh, purge=True)
        self._guid_mesh = {}

    def draw(self):
        """ Draw the skeleton and skeleton mesh in Rhino. """
        self.clear()
        self.draw_skeleton()
        self.draw_mesh()

    def draw_skeleton(self):
        self.artist.skeleton = self.datastructure

        skeleton_vertices = self.datastructure.skeleton_vertices()[0] + self.datastructure.skeleton_vertices()[1]
        skeleton_branches = self.datastructure.skeleton_branches()
        
        guids_vertices, guids_edges = self.artist.draw_skeleton(skeleton_vertices, skeleton_branches)
        self.guid_skeleton_vertices = zip(guids_vertices, skeleton_vertices)
        self.guid_skeleton_edges = zip(guids_edges, skeleton_branches)

    def draw_coarse_mesh_vertices(self):
        self.artist.skeleton = self.datastructure

        mesh_vertices_keys = list(self.datastructure.vertices())
        skeleton_vertices = self.datastructure.skeleton_vertices()[0] + self.datastructure.skeleton_vertices()[1]
        boundary_vertices = list(set(mesh_vertices_keys) - set(skeleton_vertices))
        guids = self.artist.draw_coarse_mesh_vertices(boundary_vertices)

        self.guid_coarse_mesh_vertices = zip(guids, boundary_vertices)

    def draw_mesh(self):
        self.artist.mesh = self.datastructure.to_mesh()

        key = None
        guid = self.artist.draw_mesh()
        self.guid_mesh = zip([guid], [key])


# ============================================================================
# Main
# ============================================================================

if __name__ == '__main__':
    pass
