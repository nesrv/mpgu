from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter
from schema import schema

# Создаем GraphQL роутер
graphql_app = GraphQLRouter(schema)

# Создаем приложение FastAPI
app = FastAPI(title="Messenger Channel GraphQL API")

# Подключаем GraphQL эндпоинт
app.include_router(graphql_app, prefix="/graphql")

# Health check
@app.get("/")
async def root():
    return {"message": "GraphQL API доступен на /graphql"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)