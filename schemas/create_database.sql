
-- Delete and recreate the whole database and all it's tables, every time the
-- backend starts up. This allows us to keep a consistent state while testing!
-- WARN: These tables MUST be dropped in reverse order of creation (due to relations)!

DROP TABLE IF EXISTS Reviews;
DROP TABLE IF EXISTS Orders;
DROP TABLE IF EXISTS ShoppingCarts;
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

-- Table for holding customer data.
-- role(0) == customer, role(1) == admin
CREATE TABLE Users (
	iduser INT UNIQUE NOT NULL AUTO_INCREMENT,
	role INT NOT NULL,
	email VARCHAR(45) UNIQUE NOT NULL,
	password VARCHAR(45) NOT NULL,
	first_name VARCHAR(10),
	last_name VARCHAR(10),

	PRIMARY KEY (iduser)
);

-- A connector sits at the end of a USB cable.
-- gender(0) == male, gender(1) == female
-- type is the shape/function of the connector ie: Type-C, micro-A etc.
CREATE TABLE Connectors (
	idconnector INT UNIQUE NOT NULL AUTO_INCREMENT,
	gender INT NOT NULL,
	type VARCHAR(10) NOT NULL,

	PRIMARY KEY (idconnector)
);

-- Main product table.
CREATE TABLE Products (
	idproduct INT UNIQUE NOT NULL AUTO_INCREMENT,
	price INT NOT NULL,
	in_stock INT NOT NULL,
	standard FLOAT NOT NULL,
	length FLOAT NOT NULL,
	color VARCHAR(10) NOT NULL,
	image_file VARCHAR(45),
	idconnector1 INT NOT NULL,
	idconnector2 INT NOT NULL,

	PRIMARY KEY (idproduct),
	FOREIGN KEY (idconnector1) REFERENCES Connectors(idconnector),
	FOREIGN KEY (idconnector2) REFERENCES Connectors(idconnector)
);

-- This table stores all products a logged in user wants to buy, but haven't
-- placed an order for yet.
-- Product prices should be referenced using the product ID, thus showing current
-- up to date price data.
CREATE TABLE ShoppingCarts (
	iduser INT NOT NULL,
	idproduct INT NOT NULL,
	amount INT NOT NULL,
	PRIMARY KEY (iduser, idproduct),

	-- Setting up _identifying relationship_ aka "the existence of a row in a
	-- child table (Orders) depends on a row in a parent table (Users/Products)."
	-- Source: https://stackoverflow.com/a/762994
	--
	-- More info on Foreign key syntax at:
	-- https://dev.mysql.com/doc/refman/8.0/en/create-table-foreign-keys.html
	-- Better explanation of the relational actions (ON DELETE/UPDATE) at:
	-- https://stackoverflow.com/a/6720458
	FOREIGN KEY (iduser) REFERENCES Users(iduser) ON DELETE CASCADE ON UPDATE CASCADE,
	FOREIGN KEY (idproduct) REFERENCES Products(idproduct) ON DELETE CASCADE ON UPDATE CASCADE
);

-- This table holds confirmed/historical orders, sourced from the shopping cart.
-- Once an order has been made, it's price should be made permament!
CREATE TABLE Orders (
	iduser INT NOT NULL,
	idproduct INT NOT NULL,
	amount INT NOT NULL,
	price INT NOT NULL,
	PRIMARY KEY (iduser, idproduct),

	-- As above.
	FOREIGN KEY (iduser) REFERENCES Users(iduser) ON DELETE CASCADE ON UPDATE CASCADE,
	FOREIGN KEY (idproduct) REFERENCES Products(idproduct) ON DELETE CASCADE ON UPDATE CASCADE
);

-- Allows customers to rate and comment a product, which should be shown on the
-- product page.
CREATE TABLE Reviews (
	iduser INT NOT NULL,
	idproduct INT NOT NULL,
	rating INT NOT NULL,
	comment VARCHAR(255),
	PRIMARY KEY (iduser, idproduct),

	-- See above.
	FOREIGN KEY (iduser) REFERENCES Users(iduser) ON DELETE CASCADE ON UPDATE CASCADE,
	FOREIGN KEY (idproduct) REFERENCES Products(idproduct) ON DELETE CASCADE ON UPDATE CASCADE
);

--------------------------------------------------------------------------------
-- Adds some example tuples to the tables.

INSERT INTO Users (role, email, password, first_name, last_name) VALUES
(1, "admin@localhost", "pass", "Adam", "Adminson"),
(0, "humle@home", "humle", "Humle", "Son"),
(0, "dumle@work", "dumle", "Dumle", "Dottir");

-- gender(0) == male, gender(1) == female
INSERT INTO Connectors (idconnector, gender, type) VALUES
(1, 0, "Type-A"), (2, 0, "Type-B"), (3, 1, "Type-A"), (4, 1, "Type-B");

INSERT INTO Products (price, in_stock, standard, length, color, idconnector1, idconnector2) VALUES
(199, 10, 3.0, 1.5, "black", 1, 3),
(199, 1, 3.0, 1.5, "red", 1, 3),
(99, 5, 2.0, 1.5, "black", 1, 3),
(99, 5, 2.0, 1.5, "red", 1, 3),
(99, 5, 2.0, 3.5, "black", 2, 4),
(99, 5, 2.0, 3.5, "red", 2, 4),
(59, 10, 1.5, 0.5, "black", 2, 4),
(59, 10, 1.5, 0.5, "red", 2, 4),

(199, 10, 3.0, 1.5, "black", 1, 3),
(199, 1, 3.0, 1.5, "red", 1, 3),
(99, 5, 2.0, 1.5, "black", 1, 3),
(99, 5, 2.0, 1.5, "red", 1, 3),
(99, 5, 2.0, 3.5, "black", 2, 4),
(99, 5, 2.0, 3.5, "red", 2, 4),
(59, 10, 1.5, 0.5, "black", 2, 4),
(59, 10, 1.5, 0.5, "red", 2, 4);

-- TODO: insert exampe data to shopping cart/orders/reviews when working on those features.
