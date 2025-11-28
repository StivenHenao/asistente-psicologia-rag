from chatbot.db.models import User
from chatbot.db.database import SessionLocal
from typing import List, Optional
class UserRepository:
    def __init__(self):
        self.db = SessionLocal()


    def get_all(self) -> List[User]:
        """Devuelve todos los usuarios."""
        return self.db.query(User).all()

    def get_by_id(self, user_id: int) -> Optional[User]:
        """Devuelve un usuario por su ID (la Clave Primaria)."""
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_by_email(self, email: str) -> Optional[User]:
        """Devuelve un usuario por su email (asumiendo que es único)."""
        return self.db.query(User).filter(User.email == email).first()

    def create(self, email: str, name: str, age: Optional[int] = None, city: Optional[str] = None) -> User:
        """Crea un nuevo usuario con campos obligatorios y opcionales."""
        new_user = User(
            email=email, 
            name=name, 
            age=age, 
            city=city
        )
        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)
        return new_user

    def update(self, user_id: int, **kwargs) -> Optional[User]:
        """Actualiza campos de un usuario por su ID, permitiendo actualizar múltiples campos."""
        user = self.get_by_id(user_id)
        if user:
            for key, value in kwargs.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            
            self.db.commit()
            self.db.refresh(user)
            return user
        return None
    
    def deactivate(self, user_id: int) -> Optional[User]:
        """Cambia el estado 'active' de un usuario a False."""
        return self.update(user_id, active=False)


    def delete(self, user_id: int) -> bool:
        """Elimina un usuario por su ID."""
        user = self.get_by_id(user_id)
        if user:
            self.db.delete(user)
            self.db.commit()
            return True
        return False
        
    def close(self):
        """Cierra explícitamente la sesión de la base de datos."""
        self.db.close()