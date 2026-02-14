```sh
docker run -d --name postgres18 -e POSTGRES_PASSWORD=postgres -e POSTGRES_USER=postgres -e POSTGRES_DB=postgres -p 5433:5432 postgres:18

docker exec -it postgres18 psql -U postgres -d postgres
```



