# HairlessVillager's Blog

## Useful Command Lines

- Set environment variables
  - `SECRET`: a very secret token for create or update blog, see `script.py`
  - `DROP_ALL`: if not empty, drop all tables when app start up
  - `DB_PASSWORD`: the database password
- Start PostgreSQL Docker: `docker run -d -e POSTGRES_DB=myblog -e POSTGRES_PASSWORD=<your DB_PASSWORD> -p 5432:5432 postgres`
- Start app: `uvicorn myblog:app --log-config=log_conf.yaml`
