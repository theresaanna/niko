create table users (
  id integer primary key,
  username string not null,
  email string not null,
  password string not null
);

create table entries (
  id integer primary key,
  user integer,
  mood integer,
  entry_date integer
);
