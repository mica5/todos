# todos
Structured tasks.

The goal of this code is to make it easy to export from and import to a database, and for that structured database data to support views (not necessarily "database SQL query views", but just a generic view into the tasks) that make it easier to decide which tasks to perform next.

    cp todos_config.py.example todos_config.py
    # update todos_config.py with your db credentials
    ./commands.py --create-tables
    ./commands.py --export todos.csv
    # modify todos.csv with text editor or Microsoft Excel
    ./commands.py --import todos.csv

Brand-new todos can be added as new lines in todos.csv and imported. They will be inserted into the database with their own new ids. For rows that already existed, their values in the database will found and updated based on their `tid`.
