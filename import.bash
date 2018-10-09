#!/usr/bin/env bash
this_dir="$(dirname "$(readlink -e "$0")")"
"$this_dir"/commands.py --import "$this_dir"/todo.csv
