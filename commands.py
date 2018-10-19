#!/usr/bin/env python
"""

Version 0.1
2018-10-05
"""
import sys
import os
import argparse
import datetime

from sqlalchemy import DDL
import pandas as pd

this_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(this_dir))
from todos.todos_config import engine, schema_name, connection_string
from todos.utils import get_connection

def create_tables():
    engine.execute(DDL('CREATE SCHEMA IF NOT EXISTS {schema}'.format(
        schema=schema_name,
    )))
    engine.execute(DDL('''CREATE TABLE {schema}.todos (
        tid serial primary key,
        title text not null,
        completed_at timestamp without time zone default null,
        notes text,
        created_at timestamp without time zone not null default now(),
        modified_at timestamp without time zone not null default now(),
        time_commitment int CHECK (time_commitment between 1 and 10),
        due_time timestamp without time zone,
        category text,
        person_waiting text,
        life_importance int CHECK (life_importance between 1 and 10),
        career_importance int CHECK (career_importance between 1 and 10),
        urgency int CHECK (urgency between 1 and 10),
        deleted_at timestamp without time zone default null
    )
    '''.format(
        schema=schema_name,
    )))


column_order_preference = 'completed_at due_time title'.split()
ignore_columns = 'created_at modified_at'.split()

def get_export_column_names(cursor):
    # just get the column names.. no records.
    cursor.execute('''SELECT * from {schema}.todos limit 0'''.format(schema=schema_name))
    headers = [c.name for c in cursor.description]

    # remove ignored columns
    for col in ignore_columns:
        headers.remove(col)

    # sort by column order preference
    for col in column_order_preference[::-1]:
        if col not in headers:
            continue
        headers.remove(col)
        headers.insert(0, col)

    return headers


export_tables_sql = """SELECT
        {columns}
    FROM {schema}.todos
    WHERE completed_at IS NULL AND deleted_at IS NULL
    ORDER BY
        due_time ASC NULLS LAST
        , coalesce(life_importance,0) + coalesce(career_importance,0) DESC
    """


def export_tables(filename):
    with get_connection(connection_string) as (conn, cursor):
        headers = get_export_column_names(cursor)

        df = pd.read_sql(export_tables_sql.format(
            schema=schema_name,
            columns=','.join(headers),
        ), con=conn)
        if 'due_time' in df.columns:
            df['due_time'] = df['due_time'].apply(
                lambda x:
                    '' if isinstance(x, pd._libs.tslib.NaTType)
                    else x.strftime('%Y-%m-%d %I:%M:%S %p')
            )
        df.to_excel(filename, index=False)


insert_new_todo_sql = "INSERT INTO {schema}.todos (title) values ('') RETURNING tid".format(
    schema=schema_name,
)
non_null_columns = [
    'created_at',
    'modified_at',
    'title',
]

def delete_todo(tid, run_time, cursor):
    cursor.execute(
        "UPDATE {schema}.todos SET deleted_at=%(run_time)s WHERE tid=%(tid)s".format(schema=schema_name),
        vars={
            'tid': tid,
            'run_time': run_time,
        },
    )

def import_tables(filename):
    update_query = """UPDATE {schema}.todos
        SET
            {{update_cols}}
        WHERE
            tid=%(tid)s
    """.format(
        schema=schema_name,
    )

    run_time = str(datetime.datetime.now())
    with get_connection(connection_string) as (conn, cursor):
        df = pd.read_excel(filename).fillna('')
        for i, (index, row) in enumerate(df.iterrows()):
            if i % 1000 == 0:
                conn.commit()
            new_row = row.copy()

            # convert empty string to None
            keys_to_delete = list()
            for k, v in new_row.items():

                # get rid of ="" Excel wrapper
                if isinstance(v, str) and v.startswith('="') and v.endswith('"'):
                    v = v[2:-1]
                if v in ('', 'None'):
                    v = None

                if v is None and k in non_null_columns:
                    keys_to_delete.append(k)
                    continue
                new_row[k] = v
            for k in keys_to_delete:
                new_row.pop(k)
            new_row['modified_at'] = run_time

            # make sure new entries have a new record in the DB
            # before trying to update it
            if new_row['tid'] is None:
                cursor.execute(insert_new_todo_sql)
                new_row['tid'] = cursor.fetchone()[0]

            update_cols = '\n    , '.join([
                "{colname}=%({colname})s".format(colname=colname)
                for colname in new_row.keys()
                if colname != 'tid'
            ])
            this_update_query = update_query.format(
                update_cols=update_cols,
            )
            cursor.execute(
                this_update_query,
                vars=new_row,
            )
        conn.commit()

additional_filters = "AND completed_at IS NULL AND deleted_at IS NULL"
view_queries = [
    ("due soon", """SELECT
            due_time-now() as time_until_due,title
        from {schema}.todos
        where due_time is not null
            {additional_filters}
        order by due_time asc
        limit 5"""),
    ("people waiting", """SELECT
            person_waiting,title,due_time
        from {schema}.todos
        where person_waiting is not null
            {additional_filters}
        order by due_time desc"""),
    ("urgent", """SELECT
            urgency, title
        from {schema}.todos
        where urgency is not null
            {additional_filters}
        order by urgency DESC
        limit 5"""),
    ("short time commitment", """SELECT
            time_commitment, title
        from {schema}.todos
        where time_commitment is not null
            {additional_filters}
        order by time_commitment asc
        limit 5"""),
    ("long time commitment", """SELECT
            time_commitment, title
        from {schema}.todos
        where time_commitment >= 5
            {additional_filters}
        order by time_commitment desc
        limit 5"""),
    ("life-important", """SELECT
            life_importance, title
        from {schema}.todos
        where life_importance is not null
            {additional_filters}
        order by life_importance desc
        limit 5"""),
    ("career-important", """SELECT
            career_importance, title, due_time
        from {schema}.todos
        where career_importance is not null
            {additional_filters}
        order by career_importance desc, due_time desc
        limit 5"""),
]

def view():
    import pandas as pd
    pd.options.display.expand_frame_repr = False
    with get_connection(connection_string) as (conn, cursor):
        for qname, view_query in view_queries:
            print('###################################### {} ######################################'.format(qname))
            df = pd.read_sql(
                view_query.format(
                    schema=schema_name,
                    additional_filters=additional_filters,
                ),
                con=conn
            ).fillna('')
            print(df.set_index(df.columns[0]))

def run_main():
    args = parse_cl_args()

    if args.view:
        view()
    elif args.create_tables:
        create_tables()
    elif args.export_filename:
        export_tables(args.export_filename)
    elif args.import_filename:
        import_tables(args.import_filename)

    success = True
    return success

def parse_cl_args():
    argParser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawTextHelpFormatter,
    )

    argParser.add_argument('--view', default=False, action='store_true')
    argParser.add_argument('--create-tables', default=False, action='store_true')
    argParser.add_argument(
        '--export', default=None, dest='export_filename',
        help='csv filename to export to',
    )
    argParser.add_argument(
        '--import', default=None, dest='import_filename',
        help='csv filename to import from',
    )

    args = argParser.parse_args()
    return args


if __name__ == '__main__':
    success = run_main()
    exit_code = 0 if success else 1
    exit(exit_code)
