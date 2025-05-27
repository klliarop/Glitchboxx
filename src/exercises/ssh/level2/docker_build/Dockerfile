FROM rastasheep/ubuntu-sshd:latest

ARG SSH_USERNAME
ARG SSH_PASSWORD

# Install dependencies
RUN apt update && apt install -y gcc nano make sudo

# User setup
RUN userdel -rf "$SSH_USERNAME" 2>/dev/null || true && \
    useradd -m -s /bin/bash "$SSH_USERNAME" && \
    echo "$SSH_USERNAME:$SSH_PASSWORD" | chpasswd && \
    usermod -aG sudo "$SSH_USERNAME" && \
    echo "$SSH_USERNAME ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# Security configurations
RUN echo "$SSH_USERNAME ALL=(ALL) !/bin/su, !/bin/bash, !/bin/sh, !/usr/bin/sudo su, !/usr/bin/sudo bash" >> /etc/sudoers
RUN echo "$SSH_USERNAME ALL=(ALL) NOPASSWD: /bin/chmod, /usr/bin/chown, /usr/bin/ls, /usr/bin/cat" >> /etc/sudoers

# CTF setup
RUN mkdir -p /root && \
    echo "Congrats! You got root flag!" > /root/root.txt && \
    echo "Important system file" > /root/READ_ME && \
    echo "BOUHAHA! You should have stopped me while you had the chance." > /root/Super_Reality_Override.exe && \
    chmod 600 /root/root.txt && \
    chmod 755 /root/Super_Reality_Override.exe

# SSH configuration
#RUN echo "Welcome! Only user '${SSH_USERNAME}' is allowed to connect." > /etc/issue.net
#RUN echo "Banner /etc/issue.net" >> /etc/ssh/sshd_config
#RUN echo "PermitRootLogin no" >> /etc/ssh/sshd_config


# Exercise setup
#COPY shell.c /opt/template_shell.c
#RUN chmod 644 /opt/template_shell.c

# Create user directories
#RUN mkdir -p /home/$SSH_USERNAME/Logs && \
 #   mkdir -p /home/$SSH_USERNAME/.local/share/nano && \
  #  chown -R $SSH_USERNAME:$SSH_USERNAME /home/$SSH_USERNAME

# Copy startup script
#COPY start.sh /start.sh
#RUN chmod +x /start.sh

EXPOSE 22
CMD ["/start.sh"]

