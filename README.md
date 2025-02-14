## Docker运行 API 服务器
```shell
docker pull redcomet720/an6007-group-project-api-server:latest
docker run -d -p 33468:8000 redcomet720/an6007-group-project-api-server:latest
```
## Dashboard运行
```shell
docker run -d -p 33467:8080 dashboard 
```


## TODO
批处理时，返回记录一日读数的CSV和api的log文件

定义一个api返回月度数据

日志
