from __future__ import annotations

from abc import ABC, abstractmethod


class BaseAdapter(ABC):
    @abstractmethod
    def fetch(self, *args, **kwargs):
        raise NotImplementedError
