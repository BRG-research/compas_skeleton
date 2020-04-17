********************************************************************************
Create
********************************************************************************

This user manual example takes input from Rhino and makes visulisation in Rhino.
So the codes need to be run in Rhino python editor or through CodeListener.

Create skeleton from lines
==========================

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


Create skeleton object
======================

Skeleton object contains a Skeleton as its datastructre, and a customized skeleton artist.

.. code-block:: python

    from compas_skeleton.rhino import SkeletonObject

    skeleton = Skeleton.from_json(FILE)
    skeletonobject = SkeletonObject(skeleton)
    skeletonobject.draw()

    skeletonobject.datastructure.to_json(FILE)

SkeletonObject.datastructure is a Skeleton object. So the result of the two methods below are the same. 
But after a skeleton object is created, we should always choose the second method so that all the modifications will be stored.

.. code-block:: python

    # method 1
    skeleton.to_json(FILE)

    # method 2
    skeletonobject = SkeletonObject(skeleton)
    skeletonobject.datastructure.to_json(FILE)


Edit attributes
===============

.. code-block:: python

    skeletonobject.datastructure.node_width = 20.0
    skeletonobject.datastructure.leaf_width = 10.0
    skeletonobject.datastructure.leaf_extend = -2.0
    
    skeletonobject.draw()
    skeletonobject.datastructure.to_json(FILE)


Interactive edit attributes
===========================

There are 3 steps of ``dynamic_update_mesh``: 

* click on the joint node, move cursor to decide node width
* click on the leaf vertex, move cursor to decide leaf width 
* click on the leaf vertex again, move cursor to decide how far or to which direction to extend the leaf ends.

.. code-block:: python

    skeletonobject.dynamic_update_mesh()
    skeletonobject.datastructure.to_json(FILE, pretty=True)