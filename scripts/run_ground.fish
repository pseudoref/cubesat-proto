#!/usr/bin/env fish

# go to project root (adjust manually if needed)
cd ~/projects/cubesat-proto   # <- replace with your actual path

# activate virtual environment (Fish syntax)
if test -f venv/bin/activate.fish
    source venv/bin/activate.fish
end

# set PYTHONPATH and run ground
env PYTHONPATH=. python -m ground.ground


