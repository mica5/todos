#!/usr/bin/env bash
this_dir="$(dirname "$(readlink -e "$0")")"
todo_csv_file="$this_dir"/todo.csv
./commands.py --export "$todo_csv_file" ; open "$todo_csv_file"
