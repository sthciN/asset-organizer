from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class PNGFileBudget(Base):
    __tablename__ = "png_file_budget"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    file_id = Column(String, index=True)
    budget = Column(Float, index=True)