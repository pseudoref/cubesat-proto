#!/usr/bin/env fish
cd (dirname (status --current-filename))/..
if test -f venv/bin/activate.fish
    source venv/bin/activate.fish
end
env PYTHONPATH=. python -m ground.dashboard_tui

