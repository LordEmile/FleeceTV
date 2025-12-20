from pydantic import BaseModel, ConfigDict
from api.models.enum.category import EnumCategory

class movieCreate(BaseModel):
    title : str
    release_years : str
    category : EnumCategory

class movieResponce(BaseModel):
    title : str
    category : EnumCategory
    description : str
    release_date : str
    rating : str
    poster_url : str
    updated_at : str

    model_config = ConfigDict(from_attributes=True)
