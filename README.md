## Docker运行 API 服务器
```shell
docker pull redcomet720/an6007-group-project-api-server:latest
docker run -d -p 33468:8000 redcomet720/an6007-group-project-api-server:latest
```
## Dashboard运行
```shell
docker run -d -p 33467:8080 dashboard 
```