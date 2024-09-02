from sqlalchemy.orm import Session

from . import models, schemas
from services.bids_budget.performance import adjust_budget


def get_budget(db: Session, file_id: int) -> models.PNGFileBudget:
    return db.query(models.PNGFileBudget).filter(models.PNGFileBudget.file_id == file_id).first()

def update_budget(db: Session, file_id: int, new_budget: float) -> models.PNGFileBudget:
    file_budget = get_budget(db=db, file_id=file_id)
    if not file_budget:
        # Create a new budget record in the db.
        file_budget = models.PNGFileBudget(file_id=file_id, budget=new_budget)
        db.add(file_budget)
        db.commit()
        db.refresh(file_budget)

    db.query(models.PNGFileBudget).filter(models.PNGFileBudget.file_id == file_id).update({'budget': new_budget})
    db.commit()
    
    return db.query(models.PNGFileBudget).filter(models.PNGFileBudget.file_id == file_id).first()

def budget_exists(db: Session, file_id: int) -> bool:
    return db.query(models.PNGFileBudget).filter(models.PNGFileBudget.file_id == file_id).count() > 0