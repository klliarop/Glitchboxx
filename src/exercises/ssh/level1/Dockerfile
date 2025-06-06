FROM rastasheep/ubuntu-sshd:latest

ARG SSH_USERNAME
ARG SSH_PASSWORD

# Remove existing users with UID >= 1000 (default non-system users)
RUN for user in $(awk -F: '$3 >= 1000 {print $1}' /etc/passwd); do \
  userdel -rf "$user"; \
done

# Install necessary tools
RUN apt-get update && \
    apt-get install -y unzip && \
    rm -rf /var/lib/apt/lists/*

# Add the new SSH user with given password
RUN userdel -rf "$SSH_USERNAME" 2>/dev/null || true && \
  useradd -m -s /bin/bash "$SSH_USERNAME" && \
  echo "$SSH_USERNAME:$SSH_PASSWORD" | chpasswd && \
  usermod -aG sudo "$SSH_USERNAME"

# Create the .hidden directory
RUN mkdir /home/"$SSH_USERNAME"/.hidden && \
    chmod 700 /home/"$SSH_USERNAME"/.hidden

# SSH configuration
RUN echo "Welcome! Only user '$SSH_USERNAME' is allowed here." > /etc/issue.net && \
    echo "Banner /etc/issue.net" >> /etc/ssh/sshd_config && \
    echo "PermitRootLogin no" >> /etc/ssh/sshd_config && \
    passwd -l root

# Create a startup script that removes sensitive files and starts SSH
RUN echo '#!/bin/bash\n\
rm -f /home/'"$SSH_USERNAME"'/Docs/Reality_Override.exe\n\
rm -f /home/'"$SSH_USERNAME"'/Docs/flag.txt\n\
exec /usr/sbin/sshd -D' > /start.sh && \
    chmod +x /start.sh

CMD ["/start.sh"]
