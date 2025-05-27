from abc import ABC, abstractmethod

class ExerciseConfig(ABC):
    
    @abstractmethod
    def update_docker_files(self, user, password, level):
        """Update Docker files for the exercise."""
        pass

    @abstractmethod
    def configure_level(self, level, shared_dir):
        """Configure the exercise level."""
        pass