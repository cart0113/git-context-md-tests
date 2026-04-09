"""
Base backend class for OD-DO.
"""

from abc import ABC, abstractmethod
from typing import List
from ...shapes.base import Shape


class Backend(ABC):
    @abstractmethod
    def render(self, shapes: List[Shape], output_path: str, **kwargs):
        pass
