from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import compas_rhino
from compas_rhino.artists import MeshArtist


__all__ = ['SkeletonArtist']


class SkeletonArtist(MeshArtist):
    """Artist for visualizing skeleton mesh in the Rhino model space."""
    
    def __init__(self, skeleton, layer=None, name=None):
        mesh = skeleton.to_mesh()
        super(SkeletonArtist, self).__init__(mesh)
        self.skeleton = skeleton
        self.settings.update({
            'skeleton.layer': "Skeleton::skeleton",
            'mesh.layer': "Skeleton::mesh",
            'color.skeleton.vertices': [255, 0, 0],
            'color.skeleton.edges': [0, 0, 255],
            'color.mesh.vertices': [0, 0, 0],
            'color.mesh.edges': [0, 0, 0],
            'color.mesh.faces': [0, 0, 0]
            })
        self.layer = self.settings['mesh.layer']

    def draw_skeleton(self, vertices_keys, edges_keys):
        """Draw skeleton branches in the Rhino model space."""
        points = []
        for key in vertices_keys:
            points.append({
                'pos': self.skeleton.vertex_coordinates(key),
                'name': "{}.vertex.{}".format(self.mesh.name, key),
                'color': self.settings['color.skeleton.vertices']
                })
        guids_vertices = compas_rhino.draw_points(points, layer=self.settings['skeleton.layer'], clear=False, redraw=False)

        guids_edges = []
        if edges_keys:
            lines = []
            for u, v in edges_keys:
                start = self.skeleton.vertex_coordinates(u)
                end = self.skeleton.vertex_coordinates(v)
                lines.append({
                    'start': start,
                    'end': end,
                    'name': "{}.branch.({}-{})".format(self.mesh.name, u, v),
                    'color': self.settings['color.skeleton.edges']
                    })
            guids_edges = compas_rhino.draw_lines(lines, layer=self.settings['skeleton.layer'], clear=False, redraw=False)

        return guids_vertices, guids_edges

    def draw_coarse_mesh_vertices(self, keys):
        """Draw skeleton coarse mesh vertices."""
        points = []
        for key in keys:
            points.append({
                'pos': self.skeleton.vertex_coordinates(key),
                'name': "{}.vertex.{}".format('mesh', key),
                'color': self.settings['color.mesh.vertices']
            })
        return compas_rhino.draw_points(points, layer=self.settings['mesh.layer'], clear=False, redraw=True)


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":
    pass
