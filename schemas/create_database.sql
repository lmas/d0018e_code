
-- Delete and recreate the whole database and all it's tables, every time the
-- backend starts up. This allows us to keep a consistent state while testing!

DROP TABLE IF EXISTS Connectors;
DROP TABLE IF EXISTS Products;
DROP TABLE IF EXISTS Users;
DROP TABLE IF EXISTS Orders;
DROP TABLE IF EXISTS CustomerReviews;

--------------------------------------------------------------------------------
-- Recreate all tables.

-- Default engine for MySQL v8.0 is InnoDB, per:
-- https://dev.mysql.com/doc/refman/8.0/en/storage-engine-setting.html
-- This can be changed using the following line...
-- SET default_storage_engine = INNODB;

-- TODO comment/explanation?
CREATE TABLE Connectors (
	idconnector INT NOT NULL AUTO_INCREMENT,
	gender INT NOT NULL,
	type VARCHAR(10) NOT NULL,
);

-- TODO comment/explanation?
CREATE TABLE Products (
	idproduct INT NOT NULL AUTO_INCREMENT,
	price FLOAT NOT NULL,
	in_stock INT NOT NULL,
	standard FLOAT NOT NULL,
	length FLOAT NOT NULL,
	color VARCHAR(10) NOT NULL,
	image_file VARCHAR(45),
	connector1 INT NOT NULL,
	connector2 INT NOT NULL,

	PRIMARY KEY (idproduct),
	FOREIGN KEY (connector1, connector2) REFERENCES Connectors(idconnector)
);

-- TODO comment/explanation?
CREATE TABLE Users (
	iduser INT NOT NULL AUTO_INCREMENT,
	role INT NOT NULL,
	email VARCHAR(45) NOT NULL UNIQUE, -- TODO: NOT NULL not required for UNIQUE??
	password VARCHAR(45) NOT NULL,
	first_name VARCHAR(10),
	last_name VARCHAR(10),

	PRIMARY KEY (iduser)
);

-- TODO comment/explanation?
CREATE TABLE Orders (
	iduser INT NOT NULL,
	idproduct INT NOT NULL,
	amount INT NOT NULL,
	status INT NOT NULL,

	PRIMARY KEY (iduser, idproduct),

	-- More info on FK: https://dev.mysql.com/doc/refman/8.0/en/create-table-foreign-keys.html
	FOREIGN KEY (iduser) REFERENCES Users(iduser) ON DELETE CASCADE ON UPDATE CASCADE,
	FOREIGN KEY (idproduct) REFERENCES Products(idproduct) ON DELETE CASCADE ON UPDATE CASCADE
);

-- TODO comment/explanation?
CREATE TABLE CustomerReviews (
	iduser INT NOT NULL,
	idproduct INT NOT NULL,
	rating INT NOT NULL,
	comment VARCHAR(255),

	PRIMARY KEY (iduser, idproduct),
	FOREIGN KEY (iduser) REFERENCES Users(iduser) ON DELETE CASCADE ON UPDATE CASCADE,
	FOREIGN KEY (idproduct) REFERENCES Products(idproduct) ON DELETE CASCADE ON UPDATE CASCADE
);

--------------------------------------------------------------------------------
-- Adds some example tuples to the table.

