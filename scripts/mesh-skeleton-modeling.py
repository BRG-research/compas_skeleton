"""Skeleton mesh modeling."""

import math

from compas.geometry.hull import convex_hull
from compas.geometry.spatial import orient_points

from compas.geometry import subtract_vectors
from compas.geometry import normalize_vector
from compas.geometry import add_vectors
from compas.geometry import scale_vector

from compas.datastructures.mesh import Mesh
from compas.datastructures.mesh.algorithms import subdivide_mesh_catmullclark

from compas.datastructures.network import Network

from compas_rhino.helpers.network import select_network_vertex
from compas_rhino.helpers.network import move_network_vertex
from compas_rhino.helpers.network import draw_network
from compas_rhino.helpers.mesh import draw_mesh

import rhinoscriptsyntax as rs


__author__    = ['Matthias Rippmann', ]
__copyright__ = 'Copyright 2017, BRG - ETH Zurich',
__license__   = 'MIT'
__email__     = 'rippmanm@ethz.ch'


def generate_section(radius, target_plane, reverse):
    num_p = 4  # discretization of the circle
    theta = 2 * math.pi / num_p  # angle step size
    # create cross section points around the origin
    points = [(radius * math.cos(theta * i), radius * math.sin(theta * i), 0.) for i in range(num_p)]
    # reverse points to have proper face normals
    if reverse < 0:
        points.reverse()
    # align cross section points with the edge
    return orient_points(points, target_plane=target_plane)


def generate_node(network, key, radius, fac):
    # initialize mesh object
    mesh = Mesh()
    mesh.attributes['name'] = 'mesh' + str(key)
    # coordinates of the node
    pt_cent = network.vertex_coordinates(key)
    # u's and v's of all connected edges
    edges = network.connected_edges(key)

    # loop over all edges
    section_keys = []
    for u, v in edges:
        # create vector in edge direction
        vec_nbr = subtract_vectors(network.vertex_coordinates(u), network.vertex_coordinates(v))
        # check if edges point towards or away from the node
        flag = 1
        if u == key:
            flag = -1
        # create point to locate the inner section
        pt_1 = add_vectors(pt_cent, scale_vector(vec_nbr, fac * flag))
        # create point to locate the outer section
        pt_2 = add_vectors(pt_cent, scale_vector(vec_nbr, 0.5 * flag))
        # create inner cross section points
        points = generate_section(radius, [pt_1, normalize_vector(vec_nbr)], flag)
        inner_key = [mesh.add_vertex(x=x, y=y, z=z) for x, y, z in points]
        # create outer cross section points
        points = generate_section(radius, [pt_2, normalize_vector(vec_nbr)], flag)
        outer_key = [mesh.add_vertex(x=x, y=y, z=z) for x, y, z in points]
        # create faces between inner and outer cross section
        for i in range(len(inner_key)):
            face = [inner_key[i - 1], inner_key[i], outer_key[i], outer_key[i - 1]]
            mesh.add_face(face)

        section_keys.append(inner_key)

    # vertices coordinates of all inner cross sections
    section_keys_all = [item for sublist in section_keys for item in sublist]
    points = [mesh.vertex_coordinates(key) for key in section_keys_all]
    # key index list for mapping
    key_index = [key for i, key in enumerate(section_keys_all)]
    # compute convex hull for all inner cross section points
    faces_index = convex_hull(points)
    # add convex hull faces to the mesh
    for face_index in faces_index:
        face = [key_index[i] for i in face_index]
        add_face = True

        for section_key in section_keys:
            # don't add faces for the cross section caps
            if len(set(face) & set(section_key)) == 3:
                add_face = False
                break

        if add_face:
            mesh.add_face(face)

    return mesh


# This code computes a solidified smooth mesh from a spatial network of lines.
# The shown method yields similar results as the exoskeleton plugin for Grasshopper
# to create meshes for 3D printing.

# select a network of lines
objs = rs.GetObjects("lines", 4)

radius = 0.3    # global radius for pipes
fac = 0.25      # global scale for smooth corners
sub_level = 2   # steps of subdivisions

# create network from lines in Rhino
lines = [(rs.CurveStartPoint(obj), rs.CurveEndPoint(obj)) for obj in objs]
network = Network.from_lines(lines)
rs.DeleteObjects(objs)

# start interactive loop
while True:
    rs.EnableRedraw(False)
    for key in network.vertices():
        # skip if node is not connected to any neighbor (leaf)
        if network.is_vertex_leaf(key):
            continue
        # generate mesh per node
        mesh = generate_node(network, key, radius, fac)
        # subdivide mesh
        mesh = subdivide_mesh_catmullclark(mesh, sub_level)
        # draw mesh
        draw_mesh(mesh,
                  show_faces=True,
                  show_vertices=False,
                  show_edges=False,
                  redraw=False)
    # draw network as a control skeleton
    draw_network(network)
    rs.EnableRedraw(True)
    # let the user a node
    key = select_network_vertex(network)

    if key is not None:
        # let the user move the selected node
        move_network_vertex(network, key)
    else:
        break
