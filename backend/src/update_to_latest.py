import pickle

import backend
import config

backend.connect_db()

print('Updating database to latest version...')

if input('Create oj_contests table(yes/no) : ') == 'yes':
    backend.query_db("""
    create table oj_contests
    (
        id                  integer primary key autoincrement,
        author_uid          integer not null,
        name                string not null,
        description         string not null,
        start_timestamp     integer not null,
        end_timestamp       integer not null,
        problems            string default '[]',
    )
    """)
    
backend.db.close()
