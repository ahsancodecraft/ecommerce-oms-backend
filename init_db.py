from decimal import Decimal
from database import Base, SessionLocal, engine
from models import ProductModel, UserModel  # UserModel yahan import karna zaroori hai!
from security import hash_password

def init_db():
    # 1. Database tables create karega (oms.db file ban jayegi saare tables ke sath)
    Base.metadata.create_all(bind=engine)
    print("Database tables successfully create ho gayi hain!")

    # 2. Database session start karte hain sample products aur default user add karne ke liye
    db = SessionLocal()

    # Check karein agar pehle se products mojood nahi hain toh add karein
    if not db.query(ProductModel).first():
        p1 = ProductModel(
            id=101, name="Mechanical Keyboard", price=Decimal("50.00"), _stock=10
        )
        p2 = ProductModel(
            id=102, name="Wireless Mouse", price=Decimal("25.00"), _stock=5
        )
        db.add(p1)
        db.add(p2)
        db.commit()
        print("Sample products database mein successfully add ho gaye hain!")
    else:
        print("Products pehle se database mein mojood hain.")

    # 3. Default User add karna taake testing mein asani ho
    if not db.query(UserModel).first():
        hashed_pwd = hash_password("123456")
        default_user = UserModel(
            email="ahsan@test.com", password_hash=hashed_pwd, role="customer"
        )
        db.add(default_user)
        db.commit()
        print("Default user (ahsan@test.com / 123456) successfully add ho gaya hai!")
    else:
        print("User pehle se database mein mojood hain.")

    db.close()

if __name__ == "__main__":
    init_db()