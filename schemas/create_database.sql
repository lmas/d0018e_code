
-- Delete and recreate the whole database and all it's tables, every time the
-- backend starts up. This allows us to keep a consistent state while testing!
DROP TABLE IF EXISTS Products;

CREATE TABLE Products (
	idProduct INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
	Name VARCHAR(45) NOT NULL,
	Price FLOAT NOT NULL,
	/*
	Speed INT NOT NULL,
	Length FLOAG NOT NULL,
	ImageFileName VARCHAR(45),
	Connector1 INT NOT NULL,
	Connector2 INT NOT NULL,
	Color INT NOT NULL,
	*/
);

-- Adds some example tuples to the table.
INSERT INTO Products (Name, Price) VALUES
("Long USB-A", 100),
("Short USB-A", 50);

/*
INSERT INTO Products (Name, Price, Speed, Length, ImageFileName, Connector1, Connector2, Color) VALUES
("Long USB-A", 100),
("Short USB-A", 50);
*/

