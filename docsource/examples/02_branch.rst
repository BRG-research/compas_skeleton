********************************************************************************
Branch Skeleton
********************************************************************************


.. figure:: /_images/branch_skeleton.png
    :figclass: figure
    :class: figure-img img-fluid


This example showcases the way to create a ``Skeleton`` from a set of lines and with direct attribute value input.


.. code-block:: python

    from compas_skeleton.datastructure import Skeleton
    from compas_skeleton.rhino import SkeletonObject

    lines = [
        ([0.0, 0.0, 0.0], [0.0, 10.0, 0.0]),
        ([0.0, 0.0, 0.0], [-8.6, -5.0, 0.0]),
        ([0.0, 0.0, 0.0], [8.6, -5.0, 0.0])
        ]
    skeleton = Skeleton.from_skeleton_lines(lines)
    skeleton.node_width = 4.0
    skeleton.leaf_width = 1.5
    skeleton.leaf_extend = -1.0
    skeleton.update_mesh_vertices_pos()
    skeleton.subdivide(2)

    skeletonobject = SkeletonObject(skeleton)
    skeletonobject.draw()
