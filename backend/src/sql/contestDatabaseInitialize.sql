drop table if exists oj_contest_ranking;

create table oj_contest_ranking
(
    uid                integer primary key,
    scores             string default '[]',
    final_score        integer default 0,
);