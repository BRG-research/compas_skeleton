********************************************************************************
Tutorial
********************************************************************************


Skeleton
--------
A Skeleton contains below attributes.


.. figure:: /_images/skeleton_concept_diagram.png
    :width: 100%
    :figclass: figure
    :class: figure-img img-fluid


* skeleton branches and skeleton vertices
Skeleton contains a set of lines as ``skeleton_branches``. The start and end points are stored as ``skeleton_vertices``. 
There are two typs of ``skeleton_vertices``: ``skeleton_joint`` and ``skeleton_leaf``.


* skeleton coarse mesh
Each skeleton branch halfedge generates two new vertices as ``descendent_vertices``. Together with the two ``skeleton_vertices``, they compose a mesh face.
Descendent vertices and face are then added to the skeleton coarse mesh.


* special attributes
Parameters ``node_width``, ``leaf_width``, ``leaf_extend`` represent the features of skeleton coarse mesh, respectively.


* skeleton hight-poly mesh
Skeleton high-poly mesh is the result of coarse mesh subdivision, which is decided by attribute ``sub_level``. 
``sub_leve`` can be increased or decreased during any step of modification, for a preferred visualisation. 


Create Skeleton
===============


Create Skeleton from lines:

.. code-block:: python

    from compas_skeleton.datastructure import Skeleton
    from compas_skeleton.rhino import SkeletonArtist

    lines = [
    ([0.0, 0.0, 0.0], [0.0, 10.0, 0.0]),
    ([0.0, 0.0, 0.0], [-8.6, -5.0, 0.0]),
    ([0.0, 0.0, 0.0], [8.6, -5.0, 0.0])
    ]

    skeleton = Skeleton.from_skeleton_lines(lines)
    artist = SkeletonArtist(skeleton)
    artist.draw()


Create Skeleton from a single point:

.. code-block:: python

    point = [0, 0, 0]
    skeleton = Skeleton.from_center_point(point)


Skeleton object
---------------
``SkeletonObject`` is the implementation of ``Skeleton`` in Rhino. 
Each ``SkeletonObject`` contains a ``Skeleton`` as its datastructure and a customized ``SkeletonArtist``. It can be added as a scene object.
Skeleton object provides interactive editing methods and visulisation in Rhino.


Create Skeleton Object
=======================


.. figure:: /_images/skeleton_create.gif
    :figclass: figure
    :class: figure-img img-fluid


.. code-block:: python

    from compas_skeleton.datastructure import Skeleton
    from compas_skeleton.rhino import SkeletonObject
    import compas_rhino

    guids = compas_rhino.select_lines()
    lines = compas_rhino.get_line_coordinates(guids)

    skeleton = Skeleton.from_skeleton_lines(lines)
    skeletonobject = SkeletonObject(skeleton)
    skeletonobject.draw()


Interactive input width
=======================

.. figure:: /_images/skeleton_dynamic_draw.gif
    :figclass: figure
    :class: figure-img img-fluid


.. code-block:: python

    skeletonobject.dynamic_draw_widths()


There are 3 steps of ``dynamic_draw_widths``: 

* click on the joint node, move cursor to decide node width
* click on the leaf vertex, move cursor to decide leaf width
* click on the leaf vertex again, move cursor to decide how far or to which direction to extend the leaf ends.



Serilization and reloading
==========================

Serilize the datastructure for further editing. 


.. code-block:: python

    import os

    HERE = os.path.dirname(__file__)
    FILE = os.path.join(HERE, 'skeleton.json')

    # method 1
    skeleton.to_json(FILE, pretty=True)

    # method 2
    skeletonobject.datastructure.to_json(FILE, pretty=True)


``SkeletonObject.datastructure`` is a ``Skeleton`` object. So the result of the two methods above are the same. 
But after a skeleton object is created, we should always choose the second method so that all the modifications will be stored.


Interactive editing
===================

After the skeleton mesh is created, it can be modified with interactive input.
Editing skeleton branches or changing width parameters will update related descendent vertices and as well as the entire mesh.

.. code-block:: python

    # load skeleton from previous step 
    skeleton = Skeleton.from_json(FILE)
    skeletonobject = SkeletonObject(skeleton)
    
    skeletonobject.update()

    skeletonobject.datastructure.to_json(FILE, pretty=True)


Once update mode is activated, editing methods can be called by typing command name directly in Rhino command window. Following commands are available:

node_width
**********
change the skeleton mesh width at all joint nodes.


.. figure:: /_images/skeleton_node_width.gif
    :figclass: figure
    :class: figure-img img-fluid
    :width: 80%


leaf_width
**********
change the skeleton mesh width at all leaf ends.


.. figure:: /_images/skeleton_leaf_width.gif
    :figclass: figure
    :class: figure-img img-fluid
    :width: 80%


leaf_extend
***********
change how far or to which direction to extend the leaf ends.


.. figure:: /_images/skeleton_leaf_extend.gif
    :figclass: figure
    :class: figure-img img-fluid
    :width: 80%


m_skeleton
**********
move a skeleton vertex. all related descendent vertices will be updated accordingly.


.. figure:: /_images/skeleton_m_skeleton.gif
    :figclass: figure
    :class: figure-img img-fluid
    :width: 80%


m_mesh
**********
move a mesh vertex. local transformation will be stored in the datastructure. when this vertex moves following skeleton vertex, the local movement will be transformed accordingly.


.. figure:: /_images/skeleton_m_mesh.gif
    :figclass: figure
    :class: figure-img img-fluid
    :width: 80%


subdivide
**********
increase the high poly mesh subdivision level by increasing attribute ``sub_level``


.. figure:: /_images/skeleton_merge.gif
    :figclass: figure
    :class: figure-img img-fluid
    :width: 80%


merge
**********
decrease the high poly mesh subdivision level by decreasing attribute ``sub_level``


add_lines
**********
add more lines to the current skeleton branches.


.. figure:: /_images/skeleton_add_lines.gif
    :figclass: figure
    :class: figure-img img-fluid
    :width: 80%


remove_lines
============
remove lines from the current skeleton branches.


.. figure:: /_images/skeleton_remove_lines.gif
    :figclass: figure
    :class: figure-img img-fluid
    :width: 80%


finish
======
end this round of editing and draw the resulting high-poly mesh in Rhino.


Application
-----------
Skeleton provides a way of sketching 2D diagrams and meshes from minimal inputs. 
For example, it can be used to create force patterns for `RhinoVault <https://blockresearchgroup.github.io/compas-RV2>`_ and `TNA <https://blockresearchgroup.github.io/compas_tna>`_.
