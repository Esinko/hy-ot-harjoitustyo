-- Map metadata
CREATE TABLE Meta (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
);

-- Assets
CREATE TABLE Assets (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    value BLOB NOT NULL
);

-- Map elements
CREATE TABLE Elements (
    id INTEGER PRIMARY KEY,
    name TEXT,
    x INTEGER NOT NULL,
    y INTEGER NOT NULL,
    width INTEGER NOT NULL DEFAULT 1,
    height INTEGER NOT NULL DEFAULT 1,
    rotation INTEGER NOT NULL DEFAULT 0,
    background_image INTEGER REFERENCES Assets(id) ON DELETE CASCADE DEFAULT NULL,
    background_color TEXT
);
