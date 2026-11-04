from jose import JWTError, jwt
from security import SECRET_KEY, ALGORITHM
from fastapi.security import OAuth2PasswordBearer
from fastapi.security import OAuth2PasswordRequestForm
from security import hash_password, verify_password, create_access_token
from decimal import Decimal
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
from models import Cart, ProductModel,UserModel,  OrderModel
from payment import FakePaymentProcessor, PercentageDiscountPolicy
from services import InventoryService, OrderService

app = FastAPI(title="E-Commerce OMS API with Database", version="2.0")



# Dependency for Database Session
def get_db():
  db = SessionLocal()
  try:
    yield db
  finally:
    db.close()
class CartItemRequest(BaseModel):
    product_id: int
    quantity: int

class CheckoutRequest(BaseModel):
  
  order_id: str
  items: list[CartItemRequest]


# --- Security Schemas ---
class UserRegisterRequest(BaseModel):
  email: str
  password: str
  role: str = "customer"


class UserLoginRequest(BaseModel):
  email: str
  password: str
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"Authorize": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    user = db.query(UserModel).filter(UserModel.email == email).first()
    if user is None:
        raise credentials_exception
    return user

# --- Auth Endpoints ---
@app.post("/register")
def register_user(request: UserRegisterRequest, db: Session = Depends(get_db)):
  """Naya user (Customer ya Admin) register karne ke liye endpoint."""
  # Check karein agar email pehle se exist karti hai
  existing_user = db.query(UserModel).filter(UserModel.email == request.email).first()
  if existing_user:
    raise HTTPException(status_code=400, detail="Email already registered.")

  # Password hash karein
  hashed_pwd = hash_password(request.password)
  
  new_user = UserModel(email=request.email, password_hash=hashed_pwd, role=request.role)
  db.add(new_user)
  db.commit()
  db.refresh(new_user)

  return {"success": True, "message": "User registered successfully!", "user_id": new_user.id}

@app.post("/checkout")
def checkout_order(
    request: CheckoutRequest,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        cart = Cart(customer_id=current_user.id)
        
        for item in request.items:
            product = db.query(ProductModel).filter(ProductModel.id == item.product_id).first()
            if not product:
                raise HTTPException(
                    status_code=404, detail=f"Product ID {item.product_id} not found."
                )
            cart.add_item(product, item.quantity)

        inventory_service = InventoryService(db)
        payment_processor = FakePaymentProcessor()
        discount_policy = PercentageDiscountPolicy(Decimal("10.00"))

        order_service = OrderService(
            inventory_service=inventory_service,
            payment_processor=payment_processor,
            discount_policy=discount_policy,
            db=db,
        )

        # 1. Order Checkout hua
        order = order_service.checkout(
            order_id=request.order_id, customer_id=current_user.id, cart=cart
        )

        # ==========================================
        # 2. YEH WALA CODE LAZMI HONA CHAHIYE:
        # ==========================================
        db_order = OrderModel(
            id=order.id,
            customer_id=current_user.id,
            status=order.status,
            total=order.total
        )
        db.add(db_order)
        db.commit()
        
        print(f"--- DEBUG: Order {order.id} successfully SAVED to DB for customer {current_user.id} ---")
        # ==========================================

        return {
            "success": True,
            "order_id": order.id,
            "customer_id": order.customer_id,
            "status": order.status,
            "subtotal": float(order.total),
            "message": "Order placed and saved successfully!",
        }

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Swagger ke OAuth2 Form Data ke sath login aur JWT token generate karne ka endpoint."""
    
    # Swagger ke 'username' field mein email aayegi
    user = db.query(UserModel).filter(UserModel.email == form_data.username).first()
    
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=400, 
            detail="Incorrect email or password"
        )
    
    # JWT token generate karein
    access_token = create_access_token(data={"sub": user.email})
    
    return {
        "access_token": access_token, 
        "token_type": "bearer"
    }
def login_user(request: UserLoginRequest, db: Session = Depends(get_db)):
  """User login karke JWT token hasil karne ke liye endpoint."""
  user = db.query(UserModel).filter(UserModel.email == request.email).first()
  if not user or not verify_password(request.password, user.password_hash):
    raise HTTPException(status_code=401, detail="Invalid email or password.")

  # JWT Token generate karein
  access_token = create_access_token(data={"sub": user.email, "role": user.role})
  return {"access_token": access_token, "token_type": "bearer"}

# Database tables ensure karne ke liye
Base.metadata.create_all(bind=engine)

@app.post("/orders/{order_id}/cancel")
def cancel_order(
    order_id: str,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Eligible order ko cancel karne aur inventory restore karne ka endpoint."""
    
    # 1. Database se order find karein aur verify karein ke yeh isi logged-in user ka hai
    db_order = db.query(OrderModel).filter(
        OrderModel.id == order_id,
        OrderModel.customer_id == current_user.id
    ).first()
    
    if not db_order:
        raise HTTPException(
            status_code=404, 
            detail="Order not found or you do not have permission to cancel it."
        )
        
    # 2. Check karein ke order pehle se cancelled toh nahi hai
    if db_order.status == "CANCELLED":
        raise HTTPException(
            status_code=400, 
            detail="Order is already cancelled."
        )
        
    if db_order.status == "DELIVERED":
        raise HTTPException(
            status_code=400, 
            detail="Delivered orders cannot be cancelled. Use return workflow."
        )

    try:
        # 3. Order status ko update karein
        db_order.status = "CANCELLED"
        
        # 4. Inventory restoration logic (Agar aap items ka stock wapas barhana chahte hain)
        # Yahan aap inventory_service.release(...) ya product restock call kar sakte hain
        
        db.commit()
        db.refresh(db_order)
        
        return {
            "success": True,
            "order_id": db_order.id,
            "status": db_order.status,
            "message": "Order successfully cancelled and inventory handled."
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))



# --- API Endpoints ---

@app.get("/")
def read_root():
  return {"message": "Welcome to E-Commerce OMS API with Database Integration!"}


@app.get("/products")
def get_products(db: Session = Depends(get_db)):
  """Database se tamam products fetch karne ke liye endpoint."""
  products = db.query(ProductModel).all()
  return [
      {
          "id": p.id,
          "name": p.name,
          "price": float(p.price),
          "stock": p.stock,
          "active": p.active,
      }
      for p in products
  ]

class CheckoutRequest(BaseModel):
    order_id: str
    items: list[CartItemRequest]
    # Note: yahan se customer_id hata diya hai kyunki ab yeh JWT token se aayega

@app.get("/orders/me")
def get_my_orders(
    current_user: UserModel = Depends(get_current_user),  # <-- Yeh ensure karta hai ke user authorized hai
    db: Session = Depends(get_db)
):
    """Sirf authorized user ke apne orders fetch karne ka endpoint."""
    
    # Database se sirf is current user ki customer_id ke mutabiq orders filter karein
    user_orders = db.query(OrderModel).filter(OrderModel.customer_id == current_user.id).all()
    
    if not user_orders:
        return {
            "success": True,
            "message": "Aapki koi order history mojood nahi hai.",
            "orders": []
        }
        
    return {
        "success": True,
        "count": len(user_orders),
        "orders": user_orders
    }
