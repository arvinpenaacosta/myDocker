#!/bin/bash
# Start SQL Server
/opt/mssql/bin/sqlservr &

# Wait for SQL Server to start
sleep 30s

# Run the initialization script
sqlcmd -S localhost -U sa -P "$SA_PASSWORD" -i /usr/src/app/init.sql

# Keep the container running
wait
