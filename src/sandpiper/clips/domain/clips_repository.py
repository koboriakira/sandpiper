from abc import ABC, abstractmethod

from sandpiper.clips.domain.clip import Clip, InsertedClip


class ClipsRepository(ABC):
    """Repository interface for Clips."""

    @abstractmethod
    def save(self, clip: Clip) -> InsertedClip:
        """Save a clip to the repository."""
        ...
