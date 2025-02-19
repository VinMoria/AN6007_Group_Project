# Local Run

## Start the API server:
```shell
cd backend
pip install -r requirements.txt
python app.py
```
## Start the dashboard server:
```shell
cd frontend
pip install -r requirements.txt
python dashboard.py
```

# Docker Run
## Start the API server:
```shell
docker pull redcomet720/an6007-group-project-api-server:latest
docker run -d -p 33468:8000 redcomet720/an6007-group-project-api-server:latest
```
## Start the dashboard server:
Please prepare the config.json file with the following content:
> It is crucial to note that the API Server address cannot be set to 127.0.0.1. Even if both containers are running on the same host machine, the public or private IP address of the host machine must be specified instead
```json
{
    "backend_url": "http://[your_api_server_ip]:33468"
}
```
Then run the following command:
```shell
docker pull xyw924/an6007-group-project-dash:latest
docker run -d -v [your_config_file_path]:/app/config.json -p 33467:8050 xyw924/an6007-group-project-dash:latest
```
# Simulate Request
If you want to use the **simulate_request.py** to simulate the request to inject data into the system, please first change the **server_ip** in the **simulate_request.py** file to the IP of the API server.
Then run the following command:
```shell
pip install requests
python simulate_request.py
```

