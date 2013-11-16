drop table if exists results;

create table results ( 
  map integer not null,
  user text not null,
  moves integer not null,
  time integer not null 
);