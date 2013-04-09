create table users (
  id integer primary key,
  username string not null,
  email string not null,
  password string not null,
  team integer
);

create table entries (
  id integer primary key,
  userid integer,
  username string,
  mood integer,
  entry_date integer
);

create table teams (
  id integer primary key,
  name string not null
);
