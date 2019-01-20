CREATE TABLE users
(
	uid INTEGER NOT NULL PRIMARY KEY, 
	username VARCHAR(64) NOT NULL, 
	password VARCHAR(128)
);

CREATE TABLE sku
(
	uid INTEGER NOT NULL PRIMARY KEY, 
	productline varchar(256) NOT NULL,
	caseupc INTEGER, 
	unitupc INTEGER
);

CREATE TABLE ingredients
(
	uid INTEGER NOT NULL PRIMARY KEY, 
	name varchar(128) NOT NULL, 
	description text, 
	package_size varchar(128),
	cpp INTEGER,
);

CREATE TABLE sku_to_ingredients
(
	sku_id INTEGER REFERENCES sku(uid), 
	ig_id INTEGER REFERENCES ingredients(uid),
	PRIMARY KEY(sku_id,ig_id)
);

CREATE TABLE customer
(
	uid INTEGER PRIMARY KEY, 
	name varchar(128)
);

CREATE TABLE sku_to_customer
(
	sku_id INTEGER REFERENCES sku(uid), 
	customer_id INTEGER REFERENCES customer(uid),
	PRIMARY KEY(sku_id,customer_id)
);

CREATE TABLE manufacturing_goals
(
	user_id INTEGER REFERENCES user(uid),
	sku_id INTEGER REFERENCES sku(uid),
	desired_quantity INTEGER NOT NULL, 
	PRIMARY KEY(user_id,sku_id)
);
