create table users (
    id varchar(50) not NULL,
    email varchar(50) not NULL UNIQUE,
    passwd varchar(50) not NULL,
    admin bool not NULL,
    name varchar(50) not NULL,
    image varchar(500) not NULL,
    created_at real not NULL,
    PRIMARY KEY (id)
);

create index users_idx_created_at on users(created_at);

create table blogs (
    id varchar(50) not NULL,
    user_id varchar(50) not NULL,
    user_name varchar(50) not NULL,
    user_image varchar(500) not NULL,
    title varchar(50) not NULL,
    digest varchar(50) not NULL,
    content text not NULL,
    created_at real not NULL,
    PRIMARY KEY (id)
);

create index blogs_idx_created_at on blogs(created_at);

create table comments (
    id varchar(50) not NULL,
    blog_id varchar(50) not NULL,
    user_id varchar(50) not NULL,
    user_name varchar(50) not NULL,
    user_image varchar(50) not NULL,
    content varchar(500) not NULL,
    created_at real not NULL,
    PRIMARY KEY (id)
);

create index comments_idx_created_at on comments(created_at);