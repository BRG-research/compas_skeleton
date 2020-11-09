from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from compas_skeleton.datastructure import Skeleton  # noqa: F401
from compas_rhino.artists import MeshArtist  # noqa: F401
from .skeletonartist import SkeletonArtist  # noqa: F401

MeshArtist.register(Skeleton, SkeletonArtist)

__all__ = [name for name in dir() if not name.startswith('_')]
