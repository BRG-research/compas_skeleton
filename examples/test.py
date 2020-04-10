# import compas 
# import compas_rhino
# from compas.datastructures import Mesh

# from compas_rhino.utilities import select_mesh
# from compas_rhino.artists import MeshArtist
# from compas_rhino.geometry import RhinoMesh

from compas.geometry import Frame

# f1 = Frame((0,0,0), [1,0,0], [0,1,0])
# Frame.transform()
# Frame.to_local_coords()

from compas.geometry import Transformation
f1 = Frame([1, 1, 1], [1,1,0], [-1,1,0])
f2 = Frame.worldXY()
T = Transformation.from_frame_to_frame(f2, f1)
T2 = Transformation.from_frame_to_frame(f1, f2)

from compas.geometry import Vector

vec = Vector(1, 1, 1)
vec.transform(T2)
# print(vec)

from compas.geometry import Point
frame = Frame([1, 1, 1], [0.68, 0.68, 0.27], [-0.67, 0.73, -0.15])
pw = Point(2, 2, 2) # point in wcf
# pl = frame.to_local_coords(pw)
# print(pl)
# pw = frame.to_world_coords(pl)
# print(pw)

# pl = Frame.local_to_local_coords(Frame.worldXY(), frame, pw)
# print(pl)

vec = Vector(1, 1, 0)
f1 = Frame([1, 1, 0], [1, 0 , 0], [0, 1, 0])
f2 = Frame([1, 2, 0], [1, 1, 0], [-1, 1, 0])
# vec_l = f1.to_local_coords(vec)
# vec = f2.to_world_coords(vec_l)

vec = Frame.local_to_local_coords(f2, f1, vec)

from compas.geometry import Vector

vec = Vector(0, 0, 0)
print(list(vec))