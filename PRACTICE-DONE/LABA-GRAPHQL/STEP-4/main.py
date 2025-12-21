from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter
from models_graphql import schema

# Создаем GraphQL роутер с включенным GraphQL IDE (Playground)
graphql_app = GraphQLRouter(
    schema,
    graphql_ide="graphiql",  # Включает GraphQL Playground для тестирования
)

# Создаем приложение FastAPI
app = FastAPI(
    title="Messenger Channel API",
    description="GraphQL API для информационного канала мессенджера",
    version="1.0.0",
)

# Подключаем GraphQL эндпоинт
app.include_router(graphql_app, prefix="/graphql")

# Health check
@app.get("/")
async def root():
    return {
        "message": "API доступен",
        "graphql": "/graphql",
        "graphql_playground": "/graphql (откройте в браузере)",
        "swagger": "/docs",
        "redoc": "/redoc",
    }

# Информация об API
@app.get("/info")
async def info():
    return {
        "graphql_endpoint": "/graphql",
        "graphql_playground": "Откройте /graphql в браузере для интерактивного тестирования",
        "swagger_ui": "/docs - только для REST эндпоинтов",
        "note": "GraphQL запросы тестируются через GraphQL Playground, а не Swagger",
    }

if __name__ == "__main__":
    import uvicorn
    # Для разработки с reload используйте: uvicorn main:app --reload
    uvicorn.run(app, host="0.0.0.0", port=8000)