create table users (
  id integer primary key,
  username string not null,
  email string not null
);

create table entries (
  id integer primary key,
  user integer,
  mood integer
);
