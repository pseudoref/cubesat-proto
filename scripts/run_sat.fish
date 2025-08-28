#!/usr/bin/env fish
cd (dirname (status --current-filename))/..
env PYTHONPATH=. python -m sat_sim.main

