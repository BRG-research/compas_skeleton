"""
********************************************************************************
compas_skeleton.rhino
********************************************************************************

.. currentmodule:: compas_skeleton.rhino

Artists
=======

.. autosummary::
    :toctree: generated/
    :nosignatures:

    SkeletonArtist


Objects
=======

.. autosummary::
    :toctree: generated/
    :nosignatures:

    SkeletonObject


"""
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from .artists import SkeletonArtist  # noqa: F401
from .objects import SkeletonObject  # noqa: F401


__all__ = [
    'SkeletonArtist',
    'SkeletonObject'
]
