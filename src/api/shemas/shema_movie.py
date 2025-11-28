from pydantic import BaseModel
from api.models.enum.category import EnumCategory

class movieCreate(BaseModel):
    title : str
    release_years : str
    category : EnumCategory

class movieResponce(BaseModel):
    title : str
    category : str
    description : str
    release_date : str
    rating : str
    poster_url : str
    updated_at : str

    class Config:
        from_attributes = True
