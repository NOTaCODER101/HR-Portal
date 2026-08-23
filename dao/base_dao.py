from typing import Type, TypeVar, List, Optional, Any, Dict, Generic
from config.database import db

T = TypeVar('T', bound=db.Model)

class BaseDAO(Generic[T]):
    """
    Generic Base DAO providing standard CRUD operations.
    Note: Transaction management (commit/rollback) is handled by the Service Layer.
    """
    def __init__(self, model: Type[T]):
        self.model = model

    def get_by_id(self, record_id: int) -> Optional[T]:
        """Fetch a single record by its primary key."""
        return db.session.get(self.model, record_id)

    def get_all(self, offset: int = 0, limit: Optional[int] = None) -> List[T]:
        """Fetch all records with optional pagination."""
        query = db.session.query(self.model).offset(offset)
        if limit is not None:
            query = query.limit(limit)
        return query.all()

    def add(self, record: T) -> T:
        """Add a new record to the session."""
        db.session.add(record)
        return record

    def update(self, record_id: int, update_data: Dict[str, Any]) -> Optional[T]:
        """Update an existing record with dictionary of changes."""
        record = self.get_by_id(record_id)
        if record:
            for key, value in update_data.items():
                if hasattr(record, key):
                    setattr(record, key, value)
        return record

    def delete(self, record_id: int) -> bool:
        """Delete a record by ID from the session."""
        record = self.get_by_id(record_id)
        if record:
            db.session.delete(record)
            return True
        return False
