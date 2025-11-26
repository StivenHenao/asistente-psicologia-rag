from user import User
from database import SessionLocal

class UserRepository:
    def __init__(self):
        self.db = SessionLocal()

    def get_all(self):
        return self.db.query(User).all()

    def get_by_id(self, user_id: int):
        return self.db.query(User).filter(User.user_id == user_id).first()

    def create(self, name: str, context: str):
        user = User(name=name, context=context)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def delete(self, user_id: int):
        user = self.get_by_id(user_id)
        if user:
            self.db.delete(user)
            self.db.commit()
    
    def update(self, user_id: int, context: dict):
        user = self.get_by_id(user_id)
        if user:
            user.context = context
            self.db.commit()