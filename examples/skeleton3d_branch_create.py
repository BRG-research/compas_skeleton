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


def create_sk3_quad(lines, joint_width=1, leaf_width=1, joint_length=0.4):

    def get_convex_hull_mesh(points):
        faces = convex_hull(points)
        vertices = list(set(flatten(faces)))

        i_index = {i: index for index, i in enumerate(vertices)}
        vertices = [points[index] for index in vertices]
        faces = [[i_index[i] for i in face] for face in faces]
        faces = unify_cycles(vertices, faces)

        mesh = Mesh.from_vertices_and_faces(vertices, faces)

        return mesh

    def create_networks():
        networks = {}
        descendent_tree = {}
        for u in joints:
            global_local = {}
            lines = []
            nbrs = network_global.neighbors(u)
            start_pt = network_global.node_coordinates(u)

            for v in nbrs:
                end_pt = network_global.edge_point(u, v, t=joint_length)
                lines.append([start_pt, end_pt])

            network_local = Network.from_lines(lines)
            key_local = list(set(list(network_local.nodes())) - set(network_local.leaves()))[0]
            global_local.update({u: key_local})
            
            gkeys_global_network = [geometric_key(line[1]) for line in lines]
            gkeys_local_network = [
                geometric_key(network_local.node_coordinates(key))
                for key in network_local.leaves()
                ]

            for i, key_global in enumerate(nbrs):
                gkey_global = gkeys_global_network[i]
                index_local = gkeys_local_network.index(gkey_global)
                key_local = network_local.leaves()[index_local]
                global_local.update({key_global: key_local})

            descendent_tree.update({u: global_local})
            networks.update({u: network_local})

        return networks, descendent_tree

    def create_sk3_branch(u, v):
        def find_vertices(u, v):
            sk3_joint_u = sk3_joints[u]

            # inside of network_u, find vertices on the verge
            leaf_u = descendent_tree[u][v] # this is network local key, not convexhull mesh
            leaf_u = sk3_joint_u.network_convexhull[leaf_u]
            nbrs = sk3_joint_u.convexhull_mesh.vertex_neighbors(leaf_u, ordered=True)
            keys = [sk3_joint_u.descendent_tree[leaf_u][nbr]['lp'] for nbr in nbrs]
            points = [sk3_joint_u.vertex_coordinates(key) for key in keys]

            return points

        if u in joints and v in joints:
            # its an internal edge
            points_u = find_vertices(u, v)
            points_v = find_vertices(v, u)

            if len(points_u) != len(points_v):
                mesh = get_convex_hull_mesh(points_u + points_v)
            else:
                points_v = points_v[::-1]
                index = closest_point_in_cloud(points_u[0], points_v)[2]
                points_v = points_v[index:] + points_v[:index]

                vertices = points_u + points_v
                faces = []
                n = len(points_u)
                for i in range(n):
                    faces.append(
                        [i, (i+1)%n, (i+1)%n+n, i+n]
                        )

                mesh = Mesh.from_vertices_and_faces(vertices, faces)
        
        else:
            if u in leafs:
                leaf, joint = u, v
            elif v in leafs:
                leaf, joint = v, u
            
            points_joint = find_vertices(joint, leaf)
            network = networks[joint]

            u_local = descendent_tree[joint][joint]
            v_local = descendent_tree[joint][leaf]

            vec = [
                i * (1 - joint_length) for i in network_global.edge_vector(joint, leaf)
                ]
            points_leaf = [add_vectors(pt, vec) for pt in points_joint]

            vertices = points_joint + points_leaf
            faces = []
            n = len(points_joint)
            for i in range(n):
                faces.append(
                    [i, (i+1)%n, (i+1)%n+n, i+n]
                    )

            mesh = Mesh.from_vertices_and_faces(vertices, faces)

        return mesh

    def create_sk3_branches():

        return [create_sk3_branch(u, v) for u, v in network_global.edges()]

    def create_sk3_joints(networks):
        sk3_joints = {}
        for u in networks:
            network = networks[u]
            sk3_joint = Skeleton3D_Node.from_network(network)
            sk3_joint.joint_width = joint_width
            sk3_joint.leaf_width = leaf_width
            sk3_joint.update_vertices_location()
            sk3_joints.update({u: sk3_joint})
        
        return sk3_joints

    def draw_mesh_faces(mesh):
        fkeys_nodraw = [fkey for fkey in mesh.faces() if mesh.face_area(fkey) <= 0]
        fkeys = list(set(list(mesh.faces())) - set(fkeys_nodraw))

        artist = MeshArtist(mesh)
        artist.draw_faces(faces=fkeys, join_faces=True)

    network_global = Network.from_lines(lines)

    joints = []
    leafs = []
    for key in network_global.node:
        if network_global.is_leaf(key): 
            leafs.append(key)
        else:
            joints.append(key)

    networks, descendent_tree = create_networks()
    sk3_joints = create_sk3_joints(networks)
    sk3_branches = create_sk3_branches()

    mesh = meshes_join(sk3_joints.values() + sk3_branches)
    draw_mesh_faces(mesh)

guids = compas_rhino.select_lines()
lines = compas_rhino.get_line_coordinates(guids)
<<<<<<< Updated upstream
create_sk3_quad(lines)
=======
network_global = Network.from_lines(lines)

joint_width = 0.5
leaf_width = 0.5
joint_length = 0.4

joints = []
leafs = []
for key in network_global.node:
    if network_global.is_leaf(key):
        leafs.append(key)
    else:
        joints.append(key)

networks, descendent_tree = create_networks()
sk3_joints = create_sk3_joints(networks)
sk3_branches = create_sk3_branches()

mesh = meshes_join(sk3_joints.values() + sk3_branches)
>>>>>>> Stashed changes

# artist = MeshArtist(mesh)
# # artist.draw_vertices()
# artist.draw_mesh()


# # fixed = list(sk3_node.vertices_where({'vertex_degree': 3}))
# # sk3_node = mesh_subdivide_catmullclark(sk3_node, k=1, fixed=None)
 
# sk3_node.to_json('../data/sk3_node.json', pretty=True)

