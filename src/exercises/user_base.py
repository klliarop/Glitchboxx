from abc import ABC, abstractmethod  # Import abstract base class tools

class UserExerciseBase(ABC):
    # Abstract base class for admin exercise configuration (user.py modules) for each level of exercise

    @abstractmethod
    def set_background(self, image_file):
        # Set the background image for the exercise UI
        pass

    @abstractmethod
    def start_container_for_user(self, user_id):
        # Start the Docker container for the user (or docker compose for multiple container exercises)
        pass

    @abstractmethod
    def stop_container_for_user(self, user_id):
        # Stop the Docker container for the user (or docker compose for multiple container exercises)
        pass

    @abstractmethod
    def get_container_ip(self, user_id):
        # Get the container's IP address for the user  (or returns subnet for multiple container exercises)
        pass

    @abstractmethod
    def add_firewall_rules(self, vpn_ip, container_ip):
        # Add firewall rules for the user's VPN and container IPs
        pass

    @abstractmethod
    def remove_firewall_rules(self, vpn_ip, container_ip):
        # Remove firewall rules for the user's VPN and container IPs
        pass

    @abstractmethod
    def get_user_progress_file(self, user_id):
        # Get the path to the user's progress file  (path: src/progress/service_name/level/user_id.json)
        pass

    @abstractmethod
    def save_progress(self, user_id, user_progress):
        # Save the user's progress data (path: src/progress/service_name/level/user_id.json)
        pass

    @abstractmethod
    def initialize_progress(self, user_id):
        # Initialize the user's progress data (path: src/progress/service_name/level/user_id.json)
        pass

    @abstractmethod
    def load_progress(self, user_id):
        # Load the user's progress data (path: src/progress/service_name/level/user_id.json)
        pass

    @abstractmethod
    def validate_credentials(self, user_id, step_num, question_text, correct_username, correct_password):
        # Validate credentials for a step in the exercise
        pass

    @abstractmethod
    def validate_and_update_step(self, user_id, step_num, question_text, placeholder, correct_answer):
        # Validate and update a step in the exercise
        pass

    @abstractmethod
    def validate_flag_step(self, user_id, step_num, question_text, placeholder, flag_file_relative):
        # Validate a flag step in the exercise
        pass

    @abstractmethod
    def get_vpn_ip_for_user(self, user_id, config_path="/etc/wireguard/wg0.conf"):
        # Get the VPN IP for the user from the WireGuard config
        pass