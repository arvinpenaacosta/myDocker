cls

echo     App Running @ Port 8870

uvicorn main_jwt:app --host 0.0.0.0 --port 8870 --reload --ssl-keyfile=certs/server_unencrypted.key --ssl-certfile=certs/server.crt


