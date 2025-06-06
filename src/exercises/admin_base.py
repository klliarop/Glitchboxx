from abc import ABC, abstractmethod

class AdminConfig(ABC):
    # Abstract base class for admin exercise configuration (admin_service.py modules)

    @abstractmethod
    def update_docker_files(self, user, password, level):
        """Update Docker files for the exercise."""
        pass #implementation will be provided by subclasses

    @abstractmethod
    def configure_level(self, level, shared_dir):
        """Configure the exercise level."""
        pass # implementation will be provided by subclasses
