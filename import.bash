#!/usr/bin/env bash
view_cmd=mate
which $view_cmd >/dev/null || view_cmd=less
./commands.py --import todo.csv ; ./commands.py --view | "$view_cmd"
