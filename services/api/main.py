from fastapi import FastAPI
from routers.route_search import route_search
from routers.route_file import route_file
from routers.route_movie import route_movie
from routers.route_serie import route_serie
from config.redis.redis import redis_client

app = FastAPI()
app.include_router(route_serie)
app.include_router(route_movie)
app.include_router(route_file)
app.include_router(route_search)

@app.get("/health")
def chek_health():
    return{"status":"ok"}
