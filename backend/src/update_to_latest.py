import pickle

import backend
import config

backend.connect_db()

print('Updating database to latest version...')

if input('Update oj_problem data structure(yes/no) : ') == 'yes':
    backend.query_db("alter table oj_problems add special_judge boolean default false")
    backend.query_db("alter table oj_problems add special_judge_code string default ''")
    backend.query_db("alter table oj_problems add solution string default '[]'")

if input('Create oj_articles table(yes/no) : ') == 'yes':
    backend.query_db("""
    create table oj_articles
    (
        id      integer primary key autoincrement,
        author  string not null,
        name    string not null,
        text    string not null,
        visible boolean default TRUE
    )
    """)

if input('Update user data structure(yes/no) : ') == 'yes':
    data = backend.query_db("select * from oj_users")
    for i in data:
        i['other_message'] = pickle.loads(i['other_message'])
        i['other_message']['articles_own'] = []
        i['other_message'] = pickle.dumps(i['other_message'])
        backend.query_db('update oj_users set other_message = ? where id = ?',
                         [i['other_message'], i['id']])

backend.db.close()
