********************************************************************************
Concept
********************************************************************************


Skeleton
--------
Skeleton is an extention of COMPAS Mesh with special attributes which can be serialized and loaded for modification.


skeleton branches and skeleton vertices
=======================================

.. figure:: /_images/skeleton_branches_vertices.png
    :figclass: figure
    :class: figure-img img-fluid

Skeleton contains a set of lines as ``skeleton_branches``. The start and end points are stored as ``skeleton_vertices``. 
There are two typs of ``skeleton_vertices``: ``skeleton_joint`` and ``skeleton_leaf``.


skeleton coarse mesh
====================

.. figure:: /_images/skeleton_coarse_mesh.png
    :figclass: figure
    :class: figure-img img-fluid

Each skeleton branch halfedge generates two new vertices as ``descendent_vertices``. Together with the two ``skeleton_vertices``, they compose a mesh face.
Descendent vertices and face are then added to the skeleton coarse mesh.


special attributes
==================

.. figure:: /_images/skeleton_spacial_attributes.png
    :figclass: figure
    :class: figure-img img-fluid

Parameters ``node_width``, ``leaf_width``, ``leaf_extend`` represent the features of skeleton coarse mesh, respectively.


skeleton hight-poly mesh
========================

.. figure:: /_images/skeleton_highpoly_mesh.png
    :figclass: figure
    :class: figure-img img-fluid

Skeleton high-poly mesh is the result of coarse mesh subdivision, which is decided by attribute ``sub_level``. 
``sub_leve`` can be increased or decreased during any step of modification, for a preferred visualisation. 


Skeleton object
---------------
Skeleton object is the implementation of skeleton in Rhino. 
Each skeleton object contains a Skeleton as its datastructre, and a customized skeleton artist. It can be added as a scene object.
Skeleton object provides interactive editing methods and visulisation in Rhino.


interactive editing
===================

.. figure:: /_images/skeleton_interactive_editing_02.gif
    :figclass: figure
    :class: figure-img img-fluid

After the skeleton mesh is created, it can be modified through interactive input.
Editing ``skeleton_branches`` or changing width parameters will update all the relative ``descendent_vertices`` and ultimately update the whole mesh(both coarse and high-poly).


Application
-----------
Skeleton provides a way of sketching 2D diagrams and meshes from minimal inputs. 
For example, it can be used to create force patterns for `RhinoVault <https://blockresearchgroup.github.io/compas-RV2>`_ and `TNA <https://blockresearchgroup.github.io/compas_tna>`_.
