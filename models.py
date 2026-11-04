from decimal import Decimal
from database import Base
from sqlalchemy import Boolean, Column, Numeric, String, Integer ,ForeignKey

class UserModel(Base):
  __tablename__ = "users"

  id = Column(Integer, primary_key=True, index=True)
  email = Column(String, unique=True, index=True, nullable=False)
  password_hash = Column(String, nullable=False)
  role = Column(String, default="customer")  # "customer" ya "admin"
  active = Column(Boolean, default=True)

  def __init__(self, email: str, password_hash: str, role: str = "customer",active: bool = True):
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


# Cart aur Order ki pure domain logic classes waisi hi rahengi
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
