from abc import ABC, abstractmethod

class UserExerciseBase(ABC):
    @abstractmethod
    def set_background(self, image_file):
        pass

    @abstractmethod
    def start_container_for_user(self, user_id):
        pass

    @abstractmethod
    def stop_container_for_user(self, user_id):
        pass

    @abstractmethod
    def get_container_ip(self, user_id):
        pass

    @abstractmethod
    def add_firewall_rules(self, vpn_ip, container_ip):
        pass

    @abstractmethod
    def remove_firewall_rules(self, vpn_ip, container_ip):
        pass

    @abstractmethod
    def get_user_progress_file(self, user_id):
        pass

    @abstractmethod
    def save_progress(self, user_id, user_progress):
        pass

    @abstractmethod
    def initialize_progress(self, user_id):
        pass

    @abstractmethod
    def load_progress(self, user_id):
        pass

    @abstractmethod
    def validate_credentials(self, user_id, step_num, question_text, correct_username, correct_password):
        pass

    @abstractmethod
    def validate_and_update_step(self, user_id, step_num, question_text, placeholder, correct_answer):
        pass

    @abstractmethod
    def validate_flag_step(self, user_id, step_num, question_text, placeholder, flag_file_relative):
        pass

    @abstractmethod
    def get_vpn_ip_for_user(self, user_id, config_path="/etc/wireguard/wg0.conf"):
        pass