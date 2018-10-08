#!/usr/bin/env bash
this_dir="$(dirname "$(readlink -e "$0")")"
view_cmd=mate
which $view_cmd >/dev/null || view_cmd=less
./commands.py --view | "$view_cmd"
