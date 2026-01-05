from pydantic import BaseModel, ConfigDict
from api.models.enum.category import EnumCategory
import datetime

class movieCreate(BaseModel):
    title : str
    release_years : str
    category : EnumCategory

class movieResponce(BaseModel):
    title : str
    category : EnumCategory
    description : str
    release_date : datetime.date
    rating : str
    poster_url : str
    updated_at : datetime.date

    model_config = ConfigDict(from_attributes=True)
