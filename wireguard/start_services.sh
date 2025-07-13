#!/bin/bash
sudo apt update
sudo apt install tmux

SESSION="glitchboxx"

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
VENV_ACT="source $PROJECT_ROOT/venv/bin/activate"

# Start a new tmux session
tmux new-session -d -s $SESSION

# Activate virtual environment in all windows
#VENV_ACT="source ~/jun12/Glitchboxx/venv/bin/activate"

# 1. Login Service
tmux new-window -t $SESSION:1 -n 'login'
tmux send-keys -t $SESSION:1 "$VENV_ACT && cd $PROJECT_ROOT/src/auth && python3 login.py" C-m

# 2. Register Service
tmux new-window -t $SESSION:2 -n 'register'
tmux send-keys -t $SESSION:2 "$VENV_ACT && cd $PROJECT_ROOT/src/auth && python3 register.py" C-m

# 4. Streamlit: start.py
tmux new-window -t $SESSION:4 -n 'start'
tmux send-keys -t $SESSION:4 "$VENV_ACT && cd $PROJECT_ROOT/src && streamlit run start.py" C-m

# 5. Streamlit: admin.py
tmux new-window -t $SESSION:5 -n 'admin'
tmux send-keys -t $SESSION:5 "$VENV_ACT && cd $PROJECT_ROOT/src && streamlit run admin.py" C-m

# 6. Streamlit: panel.py
tmux new-window -t $SESSION:6 -n 'panel'
tmux send-keys -t $SESSION:6 "$VENV_ACT && cd $PROJECT_ROOT/src && streamlit run panel.py" C-m

# 3. WireGuard Python Script (sudo may prompt password)
tmux new-window -t $SESSION:3 -n 'wg'
tmux send-keys -t $SESSION:3 "sudo su && $VENV_ACT && cd $PROJECT_ROOT/src/auth && python3 wg.py" C-m



# Attach to the tmux session
tmux attach -t $SESSION
