from sqlalchemy.orm import Session

from . import models, schemas


def get_budget(db: Session, file_id: int) -> models.PNGFileBudget:
    return db.query(models.PNGFileBudget).filter(models.PNGFileBudget.file_id == file_id).first()

def update_budget(db: Session, file_id: int, new_budget: float) -> models.PNGFileBudget:
    db.query(models.PNGFileBudget).filter(models.PNGFileBudget.file_id == file_id).update({'budget': new_budget})
    db.commit()
    return db.query(models.PNGFileBudget).filter(models.PNGFileBudget.file_id == file_id).first()

def create_budget(db: Session, name: str, file_id: int, budget: float) -> models.PNGFileBudget:
    file_budget = models.PNGFileBudget(name=name, file_id=file_id, budget=budget)
    db.add(file_budget)
    db.commit()
    db.refresh(file_budget)
    return file_budget

def budget_exists(db: Session, file_id: int) -> bool:
    return db.query(models.PNGFileBudget).filter(models.PNGFileBudget.file_id == file_id).count() > 0