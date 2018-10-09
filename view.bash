#!/usr/bin/env bash
this_dir="$(dirname "$(readlink -e "$0")")"

view_txt="$this_dir"/view.txt

{
    echo "$this_dir"/import.bash
    echo "$this_dir"/view.bash
    "$this_dir"/commands.py --view
} > "$view_txt"

view_cmd=mate
which $view_cmd >/dev/null || view_cmd=less
"$view_cmd" "$view_txt"
