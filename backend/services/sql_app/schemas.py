from pydantic import BaseModel, conint


class PNGFileBudgetBase(BaseModel):
    name: str
    file_id: conint(ge=0, le=99999999999999999)
    budget: float
    
    class Config:
        orm_mode = True
