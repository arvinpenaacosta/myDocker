IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'devappDB')
BEGIN
    EXEC sp_executesql N'CREATE DATABASE devappDB';
END
GO

USE devappDB;
GO

IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'entries')
BEGIN
    CREATE TABLE entries (
        id INT IDENTITY(1,1) PRIMARY KEY,
        field1 NVARCHAR(255) NOT NULL,
        field2 NVARCHAR(255) NOT NULL
    );
END
GO
