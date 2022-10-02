import pickle

import backend
import config

backend.connect_db()

print('Updating database to latest version...')

if input('Create oj_contests table(yes/no) : ') == 'yes':
    backend.db.execute("drop table if exists oj_contests")
    backend.db.execute("""
    create table oj_contests
    (
        id                  integer primary key autoincrement,
        author_uid          integer not null,
        name                string not null,
        description         string not null,
        joinable            boolean default FALSE,
        start_timestamp     integer not null,
        end_timestamp       integer not null,
        problems            string default '[]'
    )
    """)
    backend.db.execute("alter table oj_problems add column appear_time integer not null default 0")
    
backend.db.close()
