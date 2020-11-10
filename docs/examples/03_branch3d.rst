********************************************************************************
Branch Skeleton 3D 
********************************************************************************


.. figure:: /_images/branch_skeleton_3d.gif
    :figclass: figure
    :class: figure-img img-fluid


* :download:`branch_skeleton_3d.3dm <../_download/branch_skeleton_3d.3dm>`

This example showcases the way to create a ``Skeleton`` from a set of lines and with interactive input.

.. code-block:: python

    from compas_skeleton.datastructure import Skeleton
    from compas_skeleton.rhino import SkeletonObject
    import compas_rhino

    guids = compas_rhino.select_lines()  # select lines from Rhino
    lines = compas_rhino.get_line_coordinates(guids)
    compas_rhino.rs.HideObjects(guids)

    skeleton = Skeleton.from_skeleton_lines(lines)
    skeletonobject.draw()  # it draws the mesh with default width values
    skeletonobject.dynamic_draw_widths()  # move mouse cursor to change width values

    skeletonobject.update()
    # type command 'm_skeleton' to move those skeleton joint vertices up
    # tips: hold ctl and click on the vertex to move it vertically
    # type command 'subdivide' to increase subdivision level of high-poly skeleton mesh
    # type command 'finish' to exit update mode
