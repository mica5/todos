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

Finally, sample output:

    ./commands.py --view
    ################### due soon ###################
                                    title
    due_time                             
    2018-10-08         100W Slack project
    2018-10-09                 DB Midterm
    2018-10-11                   MLIS HW4
    ################### people waiting ###################
                                 title             due_time
    person_waiting                                         
    boss                       project  2018-10-08 00:00:00
    ################### short time commitment ###################
                                         title
    time_required                             
    2                       take out the trash
    ################### long time commitment ###################
                                         title
    time_required                             
    5              Dashboard url/article saver
    ################### life-important ###################
                                 title
    life_importance
    8                buy holiday gifts
    ################### career-important ###################
                                      title
    career_importance                      
    8                              MLIS HW4
