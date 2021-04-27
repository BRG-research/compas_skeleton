"""
********************************************************************************
compas_skeleton.datastructure
********************************************************************************

.. currentmodule:: compas_skeleton.datastructure

Skeleton
========

.. autosummary::
    :toctree: generated/
    :nosignatures:

    Skeleton

"""
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from .skeleton import Skeleton
from .skeleton3d import Skeleton3D
from .skeleton3d_quad import Skeleton3D_Node
# from .skeleton3d_quad import Skeleton3D_Branch


__all__ = [
    'Skeleton',
    'Skeleton3D',
    'Skeleton3D_Node'
]
