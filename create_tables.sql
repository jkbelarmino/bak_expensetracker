CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL
);
CREATE TABLE sqlite_sequence(name,seq);
CREATE TABLE expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    description TEXT NOT NULL,
    amount REAL NOT NULL,
    FOREIGN KEY (username) REFERENCES users (username)
);
