drop table if exists oj_problems;

drop table if exists oj_problem_lists;

drop table if exists oj_users;

drop table if exists oj_images;

drop table if exists oj_fileserver;

drop table if exists oj_bulletins;

drop table if exists oj_records;

drop table if exists oj_comments;

drop table if exists oj_articles;

drop table if exists oj_contests;

create table oj_problems
(
    id                 integer primary key autoincrement,
    name               string not null,
    description        string,
    examples           string,
    author             string not null,
    tags               string not null,
    timeout            int    not null default 1000,
    memory             int    not null default 65536,
    special_judge      boolean         default false,
    special_judge_code string          default '',
    solution           string          default '[]'
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
    author      integer not null,
    name        string  not null,
    description blob    not null,
    problems    string  not null
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
    points    string  default '[]' not null,
    timestamp integer not null,
    status    string  not null,
    score     integer default 0 not null
);

create table oj_comments
(
    id         integer primary key autoincrement,
    require_by string not null,
    comments   string not null -- content is a JSON structure
);

create table oj_articles
(
    id      integer primary key autoincrement,
    author  integer not null,
    name    string not null,
    text    string not null,
    visible boolean default TRUE
);

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