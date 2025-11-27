from pydantic import BaseModel

class movieCreate(BaseModel):
    title : str

class movieResponce(BaseModel):
    title : str
    category : str
    description : str
    release_date : str
    rating : str
    poster_url : str
    updated_at : str
