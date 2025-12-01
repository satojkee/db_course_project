## Build and run
> Configure `.env` file with settings before running this command. You can use `.env.example` as a template.

```shell
docker compose up -d --build
```

## Default credentials
> **Attention**: the password will be invalid in case of different API secret key.

* **username**: admin
* **password**: 11111111

## Default urls
* http://localhost:8080/
* http://localhost:8080/api/docs/redoc - Redoc documentation
* http://localhost:8080/api/docs/swagger - Swagger documentation

## Run API locally 
```shell
python3 main.py
```
