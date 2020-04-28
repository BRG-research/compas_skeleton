********************************************************************************
Dome Skeleton
********************************************************************************


.. figure:: /_images/dome_skeleton.png
    :figclass: figure
    :class: figure-img img-fluid


This example showcases the way to create a ``Skeleton`` from a single point and with direct attribute value input.
With direct input, we dont have to create a ``SkeletonObejct`` which is used to get interactive input from Rhino.


.. code-block:: python

    from compas_skeleton.datastructure import Skeleton
    from compas_skeleton.rhino import SkeletonArtist

    point = [0, 0, 0]
    skeleton = Skeleton.from_center_point(point)
    skeleton.node_width = 6.0  # set the node width
    skeleton.update_mesh_vertices_pos()  # update the descendent vertices and mesh with the new node width
    skeleton.vertex_attribute(0, 'z', 6.0)  # vertex[0] is the center point of the dome, move it up 
    skeleton.subdivide(2)

    artist = SkeletonArtist(skeleton)
    artist.draw_mesh()

