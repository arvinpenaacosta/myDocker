call ..\envApp\Scripts\Activate.bat
cls

echo     App Running @ Port 8856

uvicorn main1:app --host 192.168.1.32 --port 8856 --reload --ssl-keyfile=certs/server_unencrypted.key --ssl-certfile=certs/server.crt
