CREATE TABLE composers (
    id INTEGER NOT NULL,
    name TEXT NOT NULL,
    fullname TEXT NOT NULL,
    birthyear INTEGER NOT NULL,
    deathyear INTEGER,
    epoch TEXT NOT NULL,
    PRIMARY KEY(id)
);

CREATE TABLE works (
    id INTEGER NOT NULL,
    composer_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    solo tinyint(1) NOT NULL DEFAULT '0',  --1 means the work is for violin solo
    form TEXT NOT NULL,
    PRIMARY KEY(id),
    FOREIGN KEY (composer_id) REFERENCES composers(id)
);

CREATE TABLE users (
    id INTEGER NOT NULL,
    username TEXT NOT NULL,
    hash TEXT NOT NULL,
    PRIMARY KEY(id)
);

CREATE TABLE favorites (
    user_id INTEGER NOT NULL,
    work_id INTEGER NOT NULL,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    day INTEGER NOT NULL,
    hour INTEGER NOT NULL,
    minute INTEGER NOT NULL,
    second INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (work_id) REFERENCES works(id)
);

CREATE TABLE libraries (
    id INTEGER NOT NULL,
    lib_name TEXT NOT NULL,
    user_id INTEGER NOT NULL,
    work_id INTEGER, --All values onwards are without NOT NULL to accomodate an empty library
    year INTEGER,
    month INTEGER,
    day INTEGER,
    hour INTEGER,
    minute INTEGER,
    second INTEGER,
    PRIMARY KEY(id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (work_id) REFERENCES works(id)
);
