create table users (
   username          text primary key not null,
   passhash          text not null
);

create table user_rights (
   username          text not null,
   app_right         text not null,
   foreign key (username) references users(username)
);

create table user_attributes (
   username          text not null,
   attribute         text not null,
   foreign key (username) references users(username)
);

create table images (
   id                text primary key not null,
   mime_type         text not null,
   ts                timestamp not null
);

create table image_tags (
   id                text not null,
   tag               text not null,
   foreign key (id) references images(id)
);
create index image_id_idx on image_tags(id);
create index image_tag_idx on image_tags (tag);

