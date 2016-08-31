create table users (
   username          text primary key not null,
   passhash          text not null
);

create table user_rights (
   username          text not null,
   app_right         text not null,
   foreign key (username) references users(username)
);

create table images (
   id                string primary key not null,
   owner             text not null
);

create table image_tags (
   image_id          string not null,
   tag               string not null
);
create index image_tag_idx on image_tags (tag);

