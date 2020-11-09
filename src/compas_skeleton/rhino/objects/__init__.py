from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from compas_skeleton.datastructure import Skeleton  # noqa: F401
from compas_rhino.objects import MeshObject  # noqa: F401
from .skeletonobject import SkeletonObject  # noqa: F401

MeshObject.register(Skeleton, SkeletonObject)

__all__ = [name for name in dir() if not name.startswith('_')]
