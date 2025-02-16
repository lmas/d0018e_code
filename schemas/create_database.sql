
-- Delete and recreate the whole database and all it's tables, every time the
-- backend starts up. This allows us to keep a consistent state while testing!
DROP TABLE IF EXISTS Products;

CREATE TABLE Products (
	idProduct INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
	Name VARCHAR(45) NOT NULL,
	Price FLOAT NOT NULL,
);

-- Adds some example tuples to the table.
INSERT INTO Products (Name, Price) VALUES
("Long USB-A", 100),
("Short USB-A", 50);