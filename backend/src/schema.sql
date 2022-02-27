drop table if exists oj_problems;

drop table if exists oj_problem_lists;

drop table if exists oj_users;

drop table if exists oj_images;

drop table if exists oj_fileserver;

drop table if exists oj_bulletins;

drop table if exists oj_records;

create table oj_problems
(
    id          integer primary key autoincrement,
    name        string not null,
    description string,
    examples    string,
    author      string not null,
    tags        string not null,
    timeout     int    not null default 1000,
    memory      int    not null default 65536
);

create table oj_users
(
    id                integer primary key autoincrement,
    username          string  not null,
    password          string  not null,
    introduction      string  not null,
    full_introduction string  not null,
    ac_count          integer not null,
    other_message     blob    not null,
    user_image        blob
);

create table oj_fileserver
(
    id       integer primary key autoincrement,
    filename string not null,
    content  blob   not null
);

create table oj_problem_lists
(
    id          integer primary key autoincrement,
    name        string not null,
    description blob   not null,
    problems    string not null
);

create table oj_bulletins
(
    id      integer primary key autoincrement,
    name    string not null,
    time    string not null,
    content string not null
);

create table oj_records
(
    id        integer primary key autoincrement,
    author    integer not null,
    code      string  not null,
    lang      string  not null,
    problem   integer not null,
    points    string default '[]' not null,
    timestamp integer not null,
    status    string  not null
);