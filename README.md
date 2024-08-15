# HairlessVillager's Blog

## Manually start

- Set environment variables
  - `SECRET`: a very secret token for create or update blog, see `script.py`
  - `DROP_ALL`: if not empty, drop all tables when app start up
  - `DB_URL`: the database url, like `postgresql+asyncpg://postgres:123456@database:5432/myblog`
- Start PostgreSQL Docker: `docker run -d -e POSTGRES_DB=myblog -e POSTGRES_PASSWORD=<your DB_PASSWORD> -p 5432:5432 postgres`
- Start app: `uvicorn myblog:app --log-config=log_conf.yaml`

## Docker Compose

1. `docker-compose build`
2. `docker-compose up`

## Benchmark

`locust -f bench.py --host http://localhost:8000`

## TODOs

- replace startup command: `gunicorn myblog:app -w 4 -k uvicorn.workers.UvicornWorker`
