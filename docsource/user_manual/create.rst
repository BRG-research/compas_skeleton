********************************************************************************
Create
********************************************************************************

This user manual example takes input from Rhino and makes visulisation in Rhino.
So the codes need to be run in Rhino python editor or through CodeListener.

Create Skeleton and SkeletonObject from lines
=============================================


.. figure:: /_images/skeleton_create.gif
    :figclass: figure
    :class: figure-img img-fluid


.. code-block:: python

    from compas_skeleton.datastructure import Skeleton
    import compas_rhino
    import os

    HERE = os.path.dirname(__file__)
    FILE = os.path.join(HERE, 'skeleton.json')

    guids = compas_rhino.select_lines()
    lines = compas_rhino.get_line_coordinates(guids)

    skeleton = Skeleton.from_skeleton_lines(lines)
    skeleton.to_json(FILE, pretty=True)


Skeleton object contains a ``Skeleton`` as its datastructre, and a customized ``SkeletonArtist``.

.. code-block:: python

    from compas_skeleton.rhino import SkeletonObject

    skeleton = Skeleton.from_json(FILE)
    skeletonobject = SkeletonObject(skeleton)
    skeletonobject.draw()

    skeletonobject.datastructure.to_json(FILE)

``SkeletonObject.datastructure`` is a ``Skeleton`` object. So the result of the two methods below are the same. 
But after a skeleton object is created, we should always choose the second method so that all the modifications will be stored.

.. code-block:: python

    # method 1
    skeleton.to_json(FILE)

    # method 2
    skeletonobject = SkeletonObject(skeleton)
    skeletonobject.datastructure.to_json(FILE)


Create Skeleton and SkeletonObject from single point
====================================================


.. figure:: /_images/skeleton_dynamic_draw.gif
    :figclass: figure
    :class: figure-img img-fluid


.. code-block:: python

    from compas_skeleton.datastructure import Skeleton
    from compas_skeleton.rhino import SkeletonObject
    import compas_rhino

    guids = compas_rhino.select_points()
    point = compas_rhino.get_point_coordinates(guids)[0]

    skeleton = Skeleton.from_center_point(point)
    skeletonobject = SkeletonObject(skeleton)
    skeletonobject.draw()


Interactive input width
========================


.. figure:: /_images/skeleton_dynamic_draw.gif
    :figclass: figure
    :class: figure-img img-fluid


There are 3 steps of ``dynamic_draw_widths``: 

* click on the joint node, move cursor to decide node width
* click on the leaf vertex, move cursor to decide leaf width 
* click on the leaf vertex again, move cursor to decide how far or to which direction to extend the leaf ends.

.. code-block:: python

    skeletonobject.dynamic_draw_widths()
    skeletonobject.datastructure.to_json(FILE, pretty=True)