from pydantic import BaseModel


class PNGFileBudgetBase(BaseModel):
    name: str
    file_id: int
    budget: float
    
    class Config:
        orm_mode = True
