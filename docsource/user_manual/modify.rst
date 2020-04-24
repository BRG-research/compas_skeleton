********************************************************************************
Modify
********************************************************************************


Interactive editing
===================

Skeleton object provides interactive editing methods for the resulting mesh, by modifying the input branch lines or changing skeleton parameters.

.. code-block:: python

    skeleton = Skeleton.from_json(FILE)
    skeletonobject = SkeletonObject(skeleton)
    skeletonobject.draw()

    skeletonobject.update()
    skeletonobject.datastructure.to_json(FILE, pretty=True)


It runs editing methods in Rhino by typing command name in Rhino command line. Following commands are available:

node_width
------------


.. figure:: /_images/skeleton_node_width.gif
    :figclass: figure
    :class: figure-img img-fluid

change the skeleton mesh width at all joint nodes.


leaf_width
------------


.. figure:: /_images/skeleton_leaf_width.gif
    :figclass: figure
    :class: figure-img img-fluid


change the skeleton mesh width at all leaf ends.


leaf_extend
------------


.. figure:: /_images/skeleton_leaf_extend.gif
    :figclass: figure
    :class: figure-img img-fluid


change how far or to which direction to extend the leaf ends.


m_skeleton
-----------
move a skeleton vertex. all the relative descendent vertices will be updated.


m_mesh
-------
move a mesh vertex. local transformation will be stored in the datastructure. when this vertex moves following skeleton vertex, the local movement will be transformed accordingly.


subdivide
---------
increase the high poly mesh subdivision level by increasing attribute `sub_level`


merge
---------
decrease the high poly mesh subdivision level by decreasing attribute `sub_level`


add_lines
---------


.. figure:: /_images/skeleton_add_lines.gif
    :figclass: figure
    :class: figure-img img-fluid


add more lines to the current skeleton branches.


remove_lines
------------


.. figure:: /_images/skeleton_remove_lines.gif
    :figclass: figure
    :class: figure-img img-fluid


remove lines from the current skeleton branches.


finish
---------
end this round of editing and draw the resulting high-poly mesh in Rhino.
