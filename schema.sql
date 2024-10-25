-- This file should contain all code required to create & seed database tables.

DROP TABLE IF EXISTS rating_interaction;
DROP TABLE IF EXISTS request_interaction;
DROP TABLE IF EXISTS request;
DROP TABLE IF EXISTS rating;
DROP TABLE IF EXISTS exhibition;
DROP TABLE IF EXISTS floor;
DROP TABLE IF EXISTS department;

CREATE TABLE department (
    department_id SMALLINT GENERATED ALWAYS AS IDENTITY,
    department_name VARCHAR(100) NOT NULL,
    PRIMARY KEY (department_id)
);

CREATE TABLE floor (
    floor_id SMALLINT GENERATED ALWAYS AS IDENTITY,
    floor_name VARCHAR(100) NOT NULL,
    PRIMARY KEY (floor_id)
);

CREATE TABLE exhibition (
    exhibition_id SMALLINT GENERATED ALWAYS AS IDENTITY 
        (START WITH 0 INCREMENT BY 1 MINVALUE 0),
    exhibition_name VARCHAR(100) NOT NULL,
    exhibition_description TEXT NOT NULL,
    department_id SMALLINT NOT NULL,
    floor_id SMALLINT NOT NULL,
    exhibition_start_date DATE NOT NULL DEFAULT CURRENT_DATE,
    public_id TEXT NOT NULL,
    PRIMARY KEY (exhibition_id),
    FOREIGN KEY (department_id) REFERENCES department(department_id),
    FOREIGN KEY (floor_id) REFERENCES floor(floor_id),
    CONSTRAINT exhibition_date CHECK (exhibition_start_date <= CURRENT_DATE)
);

CREATE TABLE request (
    request_id SMALLINT GENERATED ALWAYS AS IDENTITY,
    request_value SMALLINT UNIQUE NOT NULL,
    request_description VARCHAR(100) UNIQUE NOT NULL,
    PRIMARY KEY (request_id),
    CONSTRAINT request_value_check CHECK (request_value BETWEEN 0 AND 1),
    CONSTRAINT rating_description_check 
        CHECK (request_description ILIKE 'assistance'
        OR request_description ILIKE 'emergency')
);

CREATE TABLE rating (
    rating_id SMALLINT GENERATED ALWAYS AS IDENTITY,
    rating_value SMALLINT UNIQUE DEFAULT NULL,
    rating_description VARCHAR(100) UNIQUE NOT NULL,
    PRIMARY KEY (rating_id),
    CONSTRAINT rating_value_check 
        CHECK (rating_value BETWEEN 0 AND 4)
);

CREATE TABLE request_interaction (
    request_interaction_id BIGINT GENERATED ALWAYS AS IDENTITY,
    exhibition_id SMALLINT NOT NULL,
    request_id SMALLINT DEFAULT NULL,
    event_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    PRIMARY KEY (request_interaction_id),
    FOREIGN KEY (exhibition_id) REFERENCES exhibition(exhibition_id),
    FOREIGN KEY (request_id) REFERENCES request(request_id)
);

CREATE TABLE rating_interaction (
    rating_interaction_id BIGINT GENERATED ALWAYS AS IDENTITY,
    exhibition_id SMALLINT NOT NULL,
    rating_id SMALLINT NOT NULL,
    event_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    PRIMARY KEY (rating_interaction_id),
    FOREIGN KEY (exhibition_id) REFERENCES exhibition(exhibition_id),
    FOREIGN KEY (rating_id) REFERENCES rating(rating_id)
);

INSERT INTO rating (rating_value, rating_description) VALUES
(0, 'terrible'),
(1, 'bad'),
(2, 'neutral'),
(3, 'good'),
(4, 'amazing');

INSERT INTO request (request_value, request_description) VALUES
(0, 'assistance'),
(1, 'emergency');

INSERT INTO department(department_name) VALUES
('geology'),
('entomology'),
('zoology'),
('ecology'),
('paleontology');

INSERT INTO floor(floor_name) VALUES
('vault'),
('1'),
('2'),
('3');

INSERT INTO exhibition(exhibition_name, exhibition_description, 
    department_id, floor_id, exhibition_start_date, public_id) VALUES
    ('Measureless to Man', 'An immersive 3D experience: delve deep into a previously-inaccessible cave system.' , 1, 2, TO_DATE('23/08/2021', 'DD/MM/YYYY'), 'EXH_00'),
    ('Adaption', 'How insect evolution has kept pace with an industrialised world.'
    , 2, 1, TO_DATE('01/07/2019', 'DD/MM/YYYY'), 'EXH_01'),
    ('The Crenshaw Collection', 'An exhibition of 18th Century watercolours, mostly focused on South American wildlife.',
     3, 3, TO_DATE('03/03/2021', 'DD/MM/YYYY'), 'EXH_02'),
    ('Cetacean Sensations', 'Whales: from ancient myth to critically endangered.'
     , 3, 2, TO_DATE('01/07/2019', 'DD/MM/YYYY'), 'EXH_03'),
    ('Our Polluted World', 'A hard-hitting exploration of humanity''s impact on the environment.', 4, 4, TO_DATE('12/05/2021', 'DD/MM/YYYY'), 'EXH_04'),
    ('Thunder Lizards', 'How new research is making scientists rethink what dinosaurs really looked like.', 5, 2, TO_DATE('01/02/2023', 'DD/MM/YYYY'), 'EXH_05');


