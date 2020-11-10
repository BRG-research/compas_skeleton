********************************************************************************
Loop Skeleton
********************************************************************************


.. figure:: /_images/loop_skeleton.png
    :figclass: figure
    :class: figure-img img-fluid


* :download:`loop_skeleton.3dm <../_download/loop_skeleton.3dm>`

This example showcases the way to create a ``Skeleton`` from a set of lines and with interactive input.
From the exported json file, the skeleon can be accessed and edited again.

.. code-block:: python

    from compas_skeleton.datastructure import Skeleton
    from compas_skeleton.rhino import SkeletonObject
    import compas_rhino
    import os

    guids = compas_rhino.select_lines()
    lines = compas_rhino.get_line_coordinates(guids)
    compas_rhino.rs.HideObjects(guids)

    skeleton = Skeleton.from_skeleton_lines(lines)
    skeletonobject.draw()
    skeletonobject.dynamic_draw_widths()

    HERE = os.path.dirname(__file__)
    FILE = os.path.join(HERE, 'skeleton.json')
    skeletonobject.datastructure.to_json(FILE, pretty=True)