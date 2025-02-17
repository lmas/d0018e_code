
-- Delete and recreate the whole database and all it's tables, every time the
-- backend starts up. This allows us to keep a consistent state while testing!
-- WARN: These tables MUST be dropped in reverse order of creation (due to relations)!

DROP TABLE IF EXISTS CustomerReviews;
DROP TABLE IF EXISTS Orders;
DROP TABLE IF EXISTS Products;
DROP TABLE IF EXISTS Connectors;
DROP TABLE IF EXISTS Users;

--------------------------------------------------------------------------------
-- Recreate all tables.
--
-- WARN: Last column declaration inside a CREATE TABLE must not end with a comma!
-- Extra COMMAS will fuck you up, since they produce worthless error messages!

-- Default engine for MySQL v8.0 is InnoDB, per:
-- https://dev.mysql.com/doc/refman/8.0/en/storage-engine-setting.html
-- This can be changed using the following line...
-- SET default_storage_engine = INNODB;

-- TODO comment/explanation?
CREATE TABLE Users (
	id INT UNIQUE NOT NULL AUTO_INCREMENT,
	role INT NOT NULL,
	email VARCHAR(45) UNIQUE NOT NULL,
	password VARCHAR(45) NOT NULL,
	first_name VARCHAR(10),
	last_name VARCHAR(10),

	PRIMARY KEY (id)
);

-- TODO comment/explanation?
CREATE TABLE Connectors (
	id INT UNIQUE NOT NULL AUTO_INCREMENT,
	gender INT NOT NULL,
	type VARCHAR(10) NOT NULL,

	PRIMARY KEY (id)
);

-- TODO comment/explanation?
CREATE TABLE Products (
	id INT UNIQUE NOT NULL AUTO_INCREMENT,
	price INT NOT NULL,
	in_stock INT NOT NULL,
	standard FLOAT NOT NULL,
	length FLOAT NOT NULL,
	color VARCHAR(10) NOT NULL,
	image_file VARCHAR(45),
	connector1 INT NOT NULL,
	connector2 INT NOT NULL,

	PRIMARY KEY (id),
	FOREIGN KEY (connector1) REFERENCES Connectors(id),
	FOREIGN KEY (connector2) REFERENCES Connectors(id)
);

-- TODO comment/explanation?
CREATE TABLE Orders (
	user INT NOT NULL,
	product INT NOT NULL,
	amount INT NOT NULL,
	status INT NOT NULL,
	PRIMARY KEY (user, product),

	-- Setting up _identifying relationship_ aka "the existence of a row in a
	-- child table (Orders) depends on a row in a parent table (Users/Products)."
	-- Source: https://stackoverflow.com/a/762994
	--
	-- More info on Foreign key syntax at:
	-- https://dev.mysql.com/doc/refman/8.0/en/create-table-foreign-keys.html
	-- Better explanation of the relational actions (ON DELETE/UPDATE) at:
	-- https://stackoverflow.com/a/6720458
	FOREIGN KEY (user) REFERENCES Users(id) ON DELETE CASCADE ON UPDATE CASCADE,
	FOREIGN KEY (product) REFERENCES Products(id) ON DELETE CASCADE ON UPDATE CASCADE
);

-- TODO comment/explanation?
CREATE TABLE CustomerReviews (
	user INT NOT NULL,
	product INT NOT NULL,
	rating INT NOT NULL,
	comment VARCHAR(255),
	PRIMARY KEY (user, product),

	-- See above.
	FOREIGN KEY (user) REFERENCES Users(id) ON DELETE CASCADE ON UPDATE CASCADE,
	FOREIGN KEY (product) REFERENCES Products(id) ON DELETE CASCADE ON UPDATE CASCADE
);

--------------------------------------------------------------------------------
-- Adds some example tuples to the tables.

INSERT INTO Users (role, email, password, first_name, last_name) VALUES
(1, "admin@localhost", "passw", "Adam", "Adminson"),
(0, "humle@home", "humle", "Humle", "Son"),
(0, "dumle@work", "dumle", "Dumle", "Dottir");

-- gender(0) == male, gender(1) == female
INSERT INTO Connectors (id, gender, type) VALUES
(1, 0, "Type-A"), (2, 0, "Type-B"), (3, 1, "Type-A"), (4, 1, "Type-B");

INSERT INTO Products (price, in_stock, standard, length, color, connector1, connector2) VALUES
(199, 10, 3.0, 1.5, "black", 1, 3),
(199, 1, 3.0, 1.5, "red", 1, 3),
(99, 5, 2.0, 1.5, "black", 1, 3),
(99, 5, 2.0, 1.5, "red", 1, 3),
(99, 5, 2.0, 3.5, "black", 2, 4),
(99, 5, 2.0, 3.5, "red", 2, 4),
(59, 10, 1.5, 0.5, "black", 2, 4),
(59, 10, 1.5, 0.5, "red", 2, 4);
