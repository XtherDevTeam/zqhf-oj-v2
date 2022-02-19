drop table if exists oj_problems;

drop table if exists oj_problems_data;

drop table if exists oj_problem_lists;

drop table if exists oj_users;

drop table if exists oj_images;

drop table if exists oj_fileserver;

create table oj_problems(
    id integer primary key autoincrement,
    name string not null,
    description string nit null,
    examples string nit null
);

create table oj_problems_data(
    id integer primary key autoincrement,
    inputs string not null,
    outputs string not null
);

create table oj_users(
    id integer primary key autoincrement,
    username string not null,
    password string not null,
    introduction string not null,
    full_introduction string not null
);

create table oj_fileserver(
    id integer primary key autoincrement,
    filename string not null,
    content blob not null
);

create table oj_problem_lists(
    id integer primary key autoincrement,
    name string not null,
    description blob not null,
    problems string not null
);