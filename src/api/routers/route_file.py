from fastapi import APIRouter, HTTPException

route_file = APIRouter(prefix="/file")



#modifier un dosier
@route_file.post("/{id}")
async def update_file():
    return "a venir"