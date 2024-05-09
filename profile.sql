BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "profile" (
	"UserID"	INTEGER,
	"RFID"	TEXT UNIQUE,
	"Temperature_Limit"	REAL,
	"Light_Limit"	REAL,
	"Humidity_Limit"	REAL,
	"Name"	TEXT,
	PRIMARY KEY("UserID")
);
COMMIT;
