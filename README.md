# 🚀 E-Commerce Order Management System (OMS) - Backend API

A practical, production-grade backend implementation of an E-Commerce Order Management System built using modern technologies and strict **Object-Oriented Programming (OOP)** principles[cite: 27, 28].

---

## 🌟 Project Overview & Features

This backend service handles core e-commerce workflows reliably while preventing common retail issues such as overselling, inconsistent pricing, and uncoordinated inventory changes.

* **📦 Product Catalog** ![Python](https://img.shields.io/badge/Python-3.12%2B-3776AB?style=flat-square&logo=python&logoColor=white): Manage products with strict validation on stock, pricing, and active status.
* **🔐 Secure Authentication & Authorization** ![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=flat-square&logo=fastapi&logoColor=white)[cite: 28]: JWT-based user registration and role-based access control, ensuring customers can only access and modify their own orders.
* **🛒 Shopping Cart & Checkout** ![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-D71F00?style=flat-square&logo=sqlalchemy&logoColor=white): Dynamic server-side price calculation using `Decimal`, inventory reservation, and simulated payment processing.
* **⚙️ Order Lifecycle & State Machine**: Explicit status transitions (`PENDING_PAYMENT` ➔ `CONFIRMED` / `PAYMENT_FAILED` / `CANCELLED`).
* **🔄 Reliable Cancellation Workflow**: Handle order cancellations and safe inventory restoration without duplicate restocks.
* **🧪 Automated Testing** ![Pytest](https://img.shields.io/badge/Pytest-0A7EDC?style=flat-square&logo=pytest&logoColor=white): Comprehensive unit, integration, and API test suite built with `pytest`.
---

## 🛠️ Technology Stack

| Layer | Technology & Badge | Purpose |
| :--- | :--- | :--- |
| **Language** | ![Python](https://img.shields.io/badge/Python-3.12%2B-3776AB?style=for-the-badge&logo=python&logoColor=white) | Application logic and OOP|
| **API Framework** | ![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi&logoColor=white)| HTTP routes, request validation, and interactive API docs|
| **Validation** | ![Pydantic](https://img.shields.io/badge/Pydantic-E92063?style=for-the-badge&logo=pydantic&logoColor=white)| Validate API input/output schemas |
| **Database** | ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)| Durable relational storage|
| **ORM** | ![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white)| Map Python objects to database rows|
| **Migrations** | ![Alembic](https://img.shields.io/badge/Alembic-3A7A9E?style=for-the-badge&logo=alembic&logoColor=white)| Version database schema management|
| **Testing** | ![Pytest](https://img.shields.io/badge/Pytest-0A7EDC?style=for-the-badge&logo=pytest&logoColor=white)| Unit, integration, and API tests|

---

## 📂 Project Architecture & OOP Design

The project strictly follows core Object-Oriented Design principles as outlined in the system architecture:

1. **Encapsulation** ![Python](https://img.shields.io/badge/OOP-Encapsulation-blue?style=flat-square): Domain models (`Product`, `Order`) protect internal states and prevent invalid assignments (e.g., negative stock or zero pricing) through validated methods.
2. **Polymorphism & Abstraction** ![FastAPI](https://img.shields.io/badge/Design-Polymorphism-green?style=flat-square): Payment processing uses pluggable protocols (`PaymentProcessor` protocol) allowing alternative providers like `FakePaymentProcessor`.
3. **Single Responsibility Principle (SRP)** ![SQLAlchemy](https://img.shields.io/badge/Architecture-SRP-orange?style=flat-square): Separation of concerns across database models, domain logic, service layers, and API routes.
4. **Dependency Inversion** ![Pydantic](https://img.shields.io/badge/Design-DIP-purple?style=flat-square): High-level services depend on abstractions and injected database sessions rather than concrete low-level details.

---

## 📂 Complete Project Source Code Implementation

### 1. Database Configuration (`database.py`)
```python
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "sqlite:///./oms.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
```

### 2. Security & Authentication (`security.py`)
```python
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext

SECRET_KEY = "my_super_secret_key_oms_project"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    if isinstance(password, str):
        password_bytes = password.encode('utf-8')[:72]
        password = password_bytes.decode('utf-8', errors='ignore')
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
```

### 3. Domain Models & Database Mappings (`models.py`)
```python
from decimal import Decimal
from database import Base
from sqlalchemy import Boolean, Column, Numeric, String, Integer, ForeignKey

class UserModel(Base):
  __tablename__ = "users"

  id = Column(Integer, primary_key=True, index=True)
  email = Column(String, unique=True, index=True, nullable=False)
  password_hash = Column(String, nullable=False)
  role = Column(String, default="customer")
  active = Column(Boolean, default=True)

  def __init__(self, email: str, password_hash: str, role: str = "customer", active: bool = True):
    if not email or "@" not in email:
      raise ValueError("Valid email is required")
    self.email = email
    self.password_hash = password_hash
    self.role = role
    self.active = active

class ProductModel(Base):
  __tablename__ = "products"

  id = Column(Integer, primary_key=True, index=True)
  name = Column(String, nullable=False)
  price = Column(Numeric(10, 2), nullable=False)
  _stock = Column(Integer, nullable=False, default=0)
  active = Column(Boolean, default=True)

  def __init__(self, id: int, name: str, price: Decimal, _stock: int, active: bool = True):
    if not name.strip():
      raise ValueError("Product name is required")
    if price <= Decimal("0"):
      raise ValueError("Price must be greater than zero")
    if _stock < 0:
      raise ValueError("Stock cannot be negative")
    
    self.id = id
    self.name = name
    self.price = price
    self._stock = _stock
    self.active = active

  @property
  def stock(self) -> int:
    return self._stock

  def reduce_stock(self, quantity: int) -> None:
    if isinstance(quantity, bool) or not isinstance(quantity, int):
      raise TypeError("Quantity must be an integer")
    if quantity <= 0:
      raise ValueError("Quantity must be positive")
    if quantity > self._stock:
      raise ValueError("Insufficient stock")
    self._stock -= quantity

  def restock(self, quantity: int) -> None:
    if isinstance(quantity, bool) or not isinstance(quantity, int):
      raise TypeError("Quantity must be an integer")
    if quantity <= 0:
      raise ValueError("Quantity must be positive")
    self._stock += quantity

  def deactivate(self) -> None:
    self.active = False

class CartItem:
  def __init__(self, product_id: int, quantity: int):
    if quantity <= 0:
      raise ValueError("Quantity must be a positive integer")
    self.product_id = product_id
    self.quantity = quantity

class Cart:
  def __init__(self, customer_id: int):
    self.customer_id = customer_id
    self.items: dict[int, CartItem] = {}

  def add_item(self, product: ProductModel, quantity: int) -> None:
    if not product.active:
      raise ValueError("Customers cannot purchase inactive products")
    if quantity <= 0:
      raise ValueError("Quantity must be a positive integer")
    if quantity > product.stock:
      raise ValueError("Insufficient stock available")

    if product.id in self.items:
      self.items[product.id].quantity += quantity
    else:
      self.items[product.id] = CartItem(product.id, quantity)

class OrderModel(Base):
    __tablename__ = "orders"

    id = Column(String, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(String, nullable=False)
    total = Column(Numeric(10, 2), nullable=False)

class OrderItem:
  def __init__(self, product_id: int, product_name: str, quantity: int, unit_price: Decimal):
    self.product_id = product_id
    self.product_name = product_name
    self.quantity = quantity
    self.unit_price = unit_price

  @property
  def line_total(self) -> Decimal:
    return self.unit_price * self.quantity

class Order:
  def __init__(self, id: str, customer_id: int, items: list[OrderItem]):
    if not items:
      raise ValueError("An order must contain at least one item")
    self.id = id
    self.customer_id = customer_id
    self.items = list(items)
    self.status = "PENDING_PAYMENT"

  @property
  def total(self) -> Decimal:
    return sum((item.line_total for item in self.items), Decimal("0.00"))

  def confirm(self) -> None:
    if self.status != "PENDING_PAYMENT":
      raise ValueError("Only pending orders can be confirmed")
    self.status = "CONFIRMED"

  def cancel(self) -> None:
    if self.status not in ["PENDING_PAYMENT", "CONFIRMED"]:
        raise ValueError("Only pending or confirmed orders can be cancelled")
    self.status = "CANCELLED"
        
  def mark_payment_failed(self) -> None:
    if self.status != "PENDING_PAYMENT":
      raise ValueError("Only pending orders can fail payment")
    self.status = "PAYMENT_FAILED"
```

### 4. Payment Protocols & Policies (`payment.py`)
```python
from decimal import Decimal
from typing import Protocol

class PaymentProcessor(Protocol):
  def charge(self, amount: Decimal, idempotency_key: str) -> str:
    ...

class FakePaymentProcessor:
  def charge(self, amount: Decimal, idempotency_key: str) -> str:
    if amount < Decimal("0"):
      raise ValueError("Charge amount must be positive")
    return f"fake-payment-{idempotency_key}"

class CardPaymentProcessor:
  def charge(self, amount: Decimal, idempotency_key: str) -> str:
    if amount < Decimal("0"):
      raise ValueError("Charge amount must be positive")
    return f"card-payment-reference-{idempotency_key}"

class DiscountPolicy(Protocol):
  def calculate_discount(self, subtotal: Decimal) -> Decimal:
    ...

class NoDiscountPolicy:
  def calculate_discount(self, subtotal: Decimal) -> Decimal:
    return Decimal("0.00")

class PercentageDiscountPolicy:
  def __init__(self, percentage: Decimal):
    if percentage < Decimal("0") or percentage > Decimal("100"):
      raise ValueError("Discount percentage must be between 0 and 100")
    self.percentage = percentage

  def calculate_discount(self, subtotal: Decimal) -> Decimal:
    return (subtotal * self.percentage) / Decimal("100")
```

### 5. Service Layer (`services.py`)
```python
from decimal import Decimal
from models import Cart, Order as OrderModel, OrderItem, ProductModel
from payment import DiscountPolicy, NoDiscountPolicy, PaymentProcessor
from sqlalchemy.orm import Session

class InventoryService:
  def __init__(self, db: Session):
    self.db = db

  def reserve_stock(self, cart: Cart) -> None:
    for product_id, item in cart.items.items():
      product = self.db.query(ProductModel).filter(ProductModel.id == product_id).first()
      if not product or not product.active:
        raise ValueError(f"Product ID {product_id} is inactive or does not exist.")
      if product.stock < item.quantity:
        raise ValueError(f"Insufficient stock available for {product.name}.")

    for product_id, item in cart.items.items():
      product = self.db.query(ProductModel).filter(ProductModel.id == product_id).first()
      product.reduce_stock(item.quantity)
    
    self.db.commit()

class OrderService:
  def __init__(
      self,
      inventory_service: InventoryService,
      payment_processor: PaymentProcessor,
      discount_policy: DiscountPolicy = None,
      db: Session = None,
  ):
    self.inventory_service = inventory_service
    self.payment_processor = payment_processor
    self.discount_policy = discount_policy or NoDiscountPolicy()
    self.db = db

  def checkout(self, order_id: str, customer_id: int, cart: Cart) -> OrderModel:
    if not cart.items:
      raise ValueError("Cannot checkout an empty cart.")

    order_items = []
    for product_id, cart_item in cart.items.items():
      product = self.db.query(ProductModel).filter(ProductModel.id == product_id).first()
      order_items.append(
          OrderItem(
              product_id=product.id,
              product_name=product.name,
              quantity=cart_item.quantity,
              unit_price=product.price,
          )
      )

    order = OrderModel(id=order_id, customer_id=customer_id, items=order_items)
    self.inventory_service.reserve_stock(cart)

    subtotal = order.total
    discount = self.discount_policy.calculate_discount(subtotal)
    final_amount = subtotal - discount

    try:
      payment_ref = self.payment_processor.charge(
          final_amount, idempotency_key=order.id
      )
      order.confirm()
      print(f"Checkout Successful! Payment Reference: {payment_ref}")
      return order

    except Exception as e:
      order.mark_payment_failed()
      for item in order.items:
        product = self.db.query(ProductModel).filter(ProductModel.id == item.product_id).first()
        if product:
          product.restock(item.quantity)
      self.db.commit()
      raise RuntimeError(f"Checkout failed due to payment error: {e}")
```

### 6. Database Initialization Script (`init_db.py`)
```python
from decimal import Decimal
from database import Base, SessionLocal, engine
from models import ProductModel, UserModel
from security import hash_password

def init_db():
    Base.metadata.create_all(bind=engine)
    print("Database tables successfully created!")

    db = SessionLocal()

    if not db.query(ProductModel).first():
        p1 = ProductModel(id=101, name="Mechanical Keyboard", price=Decimal("50.00"), _stock=10)
        p2 = ProductModel(id=102, name="Wireless Mouse", price=Decimal("25.00"), _stock=5)
        db.add(p1)
        db.add(p2)
        db.commit()
        print("Sample products added!")

    if not db.query(UserModel).first():
        hashed_pwd = hash_password("123456")
        default_user = UserModel(email="ahsan@test.com", password_hash=hashed_pwd, role="customer")
        db.add(default_user)
        db.commit()
        print("Default user added (ahsan@test.com / 123456)")

    db.close()

if __name__ == "__main__":
    init_db()
```

### 7. FastAPI Routing & Endpoints (`main.py`)
```python
from jose import JWTError, jwt
from security import SECRET_KEY, ALGORITHM
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from security import hash_password, verify_password, create_access_token
from decimal import Decimal
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
from models import Cart, ProductModel, UserModel, OrderModel
from payment import FakePaymentProcessor, PercentageDiscountPolicy
from services import InventoryService, OrderService

app = FastAPI(title="E-Commerce OMS API with Database", version="2.0")

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

@app.post("/register")
def register_user(request: UserRegisterRequest, db: Session = Depends(get_db)):
  existing_user = db.query(UserModel).filter(UserModel.email == request.email).first()
  if existing_user:
    raise HTTPException(status_code=400, detail="Email already registered.")

  hashed_pwd = hash_password(request.password)
  new_user = UserModel(email=request.email, password_hash=hashed_pwd, role=request.role)
  db.add(new_user)
  db.commit()
  db.refresh(new_user)
  return {"success": True, "message": "User registered successfully!", "user_id": new_user.id}

@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

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
                raise HTTPException(status_code=404, detail=f"Product ID {item.product_id} not found.")
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

        order = order_service.checkout(
            order_id=request.order_id, customer_id=current_user.id, cart=cart
        )

        db_order = OrderModel(
            id=order.id,
            customer_id=current_user.id,
            status=order.status,
            total=order.total
        )
        db.add(db_order)
        db.commit()

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

Base.metadata.create_all(bind=engine)

@app.post("/orders/{order_id}/cancel")
def cancel_order(
    order_id: str,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_order = db.query(OrderModel).filter(
        OrderModel.id == order_id,
        OrderModel.customer_id == current_user.id
    ).first()
    
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found or permission denied.")
    if db_order.status == "CANCELLED":
        raise HTTPException(status_code=400, detail="Order is already cancelled.")

    try:
        db_order.status = "CANCELLED"
        db.commit()
        db.refresh(db_order)
        return {"success": True, "order_id": db_order.id, "status": db_order.status, "message": "Order successfully cancelled."}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def read_root():
  return {"message": "Welcome to E-Commerce OMS API with Database Integration!"}

@app.get("/products")
def get_products(db: Session = Depends(get_db)):
  products = db.query(ProductModel).all()
  return [{"id": p.id, "name": p.name, "price": float(p.price), "stock": p.stock, "active": p.active} for p in products]

@app.get("/orders/me")
def get_my_orders(
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user_orders = db.query(OrderModel).filter(OrderModel.customer_id == current_user.id).all()
    if not user_orders:
        return {"success": True, "message": "No order history found.", "orders": []}
    return {"success": True, "count": len(user_orders), "orders": user_orders}
```

### 8. Automated Pytest Suite (`test_oms.py`)
```python
from decimal import Decimal
from fastapi.testclient import TestClient
from main import app
from models import ProductModel, Cart, Order, OrderItem
from payment import PercentageDiscountPolicy
import pytest

client = TestClient(app)

def test_read_root():
  response = client.get("/")
  assert response.status_code == 200
  assert "Welcome" in response.json()["message"]

def test_get_products():
  response = client.get("/products")
  assert response.status_code == 200
  data = response.json()
  assert isinstance(data, list)

def test_product_stock_reduction():
  keyboard = ProductModel(id=101, name="Mechanical Keyboard", price=Decimal("50.00"), _stock=10)
  assert keyboard.stock == 10
  keyboard.reduce_stock(3)
  assert keyboard.stock == 7

def test_percentage_discount_policy():
  policy = PercentageDiscountPolicy(Decimal("10.00"))
  subtotal = Decimal("200.00")
  discount = policy.calculate_discount(subtotal)
  assert discount == Decimal("20.00")

def test_product_rejects_overselling():
    product = ProductModel(1, "Mouse", Decimal("20.00"), 2)
    with pytest.raises(ValueError, match="Insufficient stock"):
        product.reduce_stock(3)
    assert product.stock == 2

def test_order_cancellation_rules():
    keyboard = ProductModel(101, "Keyboard", Decimal("45.00"), 10)
    item = OrderItem(keyboard.id, keyboard.name, 2, keyboard.price)
    order = Order("ORD-1001", customer_id=7, items=[item])
    assert order.status == "PENDING_PAYMENT"
    order.cancel()
    assert order.status == "CANCELLED"
```

## 🔄 Order Lifecycle & State Rules ![FastAPI](https://img.shields.io/badge/State-Machine-blue?style=flat-square&logo=fastapi&logoColor=white)

The system implements explicit state machine transitions to maintain consistency:

* `PENDING_PAYMENT` ![Status](https://img.shields.io/badge/Status-Pending%20Payment-yellow?style=flat-square) ➔ `CONFIRMED` ![Status](https://img.shields.io/badge/Status-Confirmed-green?style=flat-square) (Payment verified successful)
* `PENDING_PAYMENT` ![Status](https://img.shields.io/badge/Status-Pending%20Payment-yellow?style=flat-square) ➔ `PAYMENT_FAILED` ![Status](https://img.shields.io/badge/Status-Payment%20Failed-red?style=flat-square) (Payment definitively failed)
* `PENDING_PAYMENT` ![Status](https://img.shields.io/badge/Status-Pending%20Payment-yellow?style=flat-square) ➔ `CANCELLED` ![Status](https://img.shields.io/badge/Status-Cancelled-orange?style=flat-square) (Cancellation allowed, reservation released)
* `CONFIRMED` ![Status](https://img.shields.io/badge/Status-Confirmed-green?style=flat-square) ➔ `CANCELLED` ![Status](https://img.shields.io/badge/Status-Cancelled-orange?style=flat-square) (Policy allowed; coordinates refund and inventory restoration)

---



## ⚙️ Installation & Setup Instructions

### 1. Clone & Navigate
Clone the repository or open the project folder in VS Code.

### 2. Create Virtual Environment
```bash
python -m venv venv
```
### 3. Install Dependencies
```bash
    python -m pip install fastapi uvicorn sqlalchemy pydantic pydantic-settings 
```
### 4. Initialize Database
```bash 
    python init_db.py
 ```
### 🚀 Running the Application

### * Start the development server using Uvicorn:
```bash
   uvicorn main:app --reload
```
### * Open your browser and explore the interactive Swagger UI documentation:
```go to
👉  http://127.0.0.1:8000/docs
```
### 🧪 Running Tests To run the automated test suite and verify business rules(At VS-Code Terminal):
```bash
    pytest
```
### 📌 Main API Endpoints

| Method | Endpoint | Description | Access |
| :--- | :--- | :--- | :--- |
| **POST** | `/register` | Register a new customer | Public |
| **POST** | `/login` | Authenticate and obtain JWT token | Public |
| **GET** | `/products` | List active catalog products | Public |
| **POST** | `/checkout` | Submit cart items and place order | Authenticated |
| **GET** | `/orders/me` | Fetch logged-in user's order history | Authenticated |
| **POST** | `/orders/{id}/cancel` | Cancel Orders/Restore Inventory | Authenticated |