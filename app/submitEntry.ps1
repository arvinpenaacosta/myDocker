# Define the URL of your FastAPI endpoint
$Url = "https://192.168.1.32:8872/api/submit2"

# Define the data to send in the request body
$Data = @{
    field1 = "arvin"
    field2 = "powershell"
}

# Convert the data to JSON format
$JsonData = $Data | ConvertTo-Json

# Send the POST request to the FastAPI endpoint
[System.Net.ServicePointManager]::ServerCertificateValidationCallback = {$true}
$response = Invoke-RestMethod -Uri $Url -Method POST -Body $JsonData -ContentType 'application/json'

# Output the response from the API
$response
