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


__all__ = [name for name in dir() if not name.startswith('_')]
