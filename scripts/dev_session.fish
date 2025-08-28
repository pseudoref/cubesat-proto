#!/usr/bin/env fish
kitty new-session \; \
  send-keys './scripts/run_ground.fish' C-m \; \
  split-window -v \; \
  send-keys './scripts/run_sat.fish' C-m \; \
  split-window -h \; \
  send-keys './scripts/run_dashboard.fish' C-m \; \
  select-pane -t 0

