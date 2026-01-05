from fastapi import FastAPI
from api.routers.route_search import route_search
from api.routers.route_file import route_file
from api.routers.route_movie import route_movie
from api.routers.route_serie import route_serie

app = FastAPI()
app.include_router(route_serie)
app.include_router(route_movie)
app.include_router(route_file)
app.include_router(route_search)

@app.get("/health")
def chek_health():
    return{"status":"ok"}