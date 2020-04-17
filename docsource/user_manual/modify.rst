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


It calls editing methods from Rhino by typing command name in Rhino command line. Following commands are available:

node_width
------------
change the skeleton mesh width at all joint nodes.


leaf_width
------------
change the skeleton mesh width at all leaf ends.


leaf_extend
------------
change how far or to which direction to extend the leaf ends.


m_skeleton
-------
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
add more lines to the current skeleton branches.


remove_lines
---------
remove lines from the current skeleton branches.


finish
---------
end this round of editing and draw the resulting high-poly mesh in Rhino.