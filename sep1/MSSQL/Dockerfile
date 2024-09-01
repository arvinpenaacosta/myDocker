# Use the official Microsoft SQL Server image from the Microsoft Container Registry

FROM mcr.microsoft.com/mssql/server:2022-latest

# Set environment variable to accept the SQL Server license agreement
ENV ACCEPT_EULA=Y

# Expose SQL Server port
EXPOSE 1433

# Optionally, copy any initialization scripts or configuration files into the container
# COPY ./init.sql /var/opt/mssql/init.sql

# Run SQL Server as the container's main process
CMD ["/opt/mssql/bin/sqlservr"]
