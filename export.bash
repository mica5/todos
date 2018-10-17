#!/usr/bin/env bash
this_dir="$(dirname "$(readlink -e "$0")")"
todo_excel_file="$this_dir"/todo.xlsx
"$this_dir"/commands.py --export "$todo_excel_file" ; open "$todo_excel_file"
