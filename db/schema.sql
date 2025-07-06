DROP TABLE IF EXISTS monster_terrains, monster_tags, monster_types, movesets, evolutions, history, monsters, types, tags, terrains CASCADE;

-- Core
CREATE TABLE monsters (
    id SERIAL PRIMARY KEY,
    slug TEXT UNIQUE,
    category TEXT,
    shape TEXT,
    stage TEXT,
    height INT,
    weight INT,
    catch_rate FLOAT,
    lower_catch_resistance FLOAT,
    upper_catch_resistance FLOAT
);

-- Types
CREATE TABLE types (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE
);

CREATE TABLE monster_types (
    monster_id INT REFERENCES monsters(id),
    type_id INT REFERENCES types(id),
    PRIMARY KEY (monster_id, type_id)
);

-- Tags
CREATE TABLE tags (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE
);

CREATE TABLE monster_tags (
    monster_id INT REFERENCES monsters(id),
    tag_id INT REFERENCES tags(id),
    PRIMARY KEY (monster_id, tag_id)
);

-- Terrains
CREATE TABLE terrains (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE
);

CREATE TABLE monster_terrains (
    monster_id INT REFERENCES monsters(id),
    terrain_id INT REFERENCES terrains(id),
    PRIMARY KEY (monster_id, terrain_id)
);

-- Movesets
CREATE TABLE movesets (
    id SERIAL PRIMARY KEY,
    monster_id INT REFERENCES monsters(id),
    level_learned INT,
    technique TEXT
);

-- Evolutions
CREATE TABLE evolutions (
    id SERIAL PRIMARY KEY,
    monster_id INT REFERENCES monsters(id),
    at_level INT,
    evolves_to_slug TEXT
);

-- History
CREATE TABLE history (
    id SERIAL PRIMARY KEY,
    monster_id INT REFERENCES monsters(id),
    mon_slug TEXT,
    evo_stage TEXT
);

-- Teams
CREATE TABLE teams (
    id SERIAL PRIMARY KEY,
    team_name TEXT UNIQUE,
    created_at TIMESTAMP
);

-- Team Members
CREATE TABLE team_members (
    team_id INT REFERENCES teams(id),
    tuxemon_id INT REFERENCES monsters(id),
    PRIMARY KEY (team_id, tuxemon_id)
);
