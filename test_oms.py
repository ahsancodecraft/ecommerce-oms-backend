from decimal import Decimal
from fastapi.testclient import TestClient
from main import app
from models import ProductModel, Cart,Order,OrderItem
from payment import PercentageDiscountPolicy
import pytest
# FastAPI TestClient initialize karna API endpoints test karne ke liye
client = TestClient(app)


def test_read_root():
  """Root endpoint ko test karne ke liye."""
  response = client.get("/")
  assert response.status_code == 200
  assert "Welcome" in response.json()["message"]


def test_get_products():
  """Products list endpoint ko test karne ke liye."""
  response = client.get("/products")
  assert response.status_code == 200
  data = response.json()
  assert isinstance(data, list)
  assert len(data) > 0


def test_product_stock_reduction():
  """Product stock rules aur decrease logic test karne ke liye."""
  keyboard = ProductModel(
      id=101, name="Mechanical Keyboard", price=Decimal("50.00"), _stock=10
  )
  assert keyboard.stock == 10

  keyboard.reduce_stock(3)
  assert keyboard.stock == 7


def test_percentage_discount_policy():
  """Discount calculation logic test karne ke liye (Phase 2)."""
  policy = PercentageDiscountPolicy(Decimal("10.00"))  # 10% discount
  subtotal = Decimal("200.00")
  discount = policy.calculate_discount(subtotal)
  
  assert discount == Decimal("20.00")

  def test_register_user():
    """/register endpoint ko test karne ke liye."""
    response = client.post(
        "/register",
        json={
            "email": "pytest_user@test.com",
            "password": "password123",
            "role": "customer"
        }
    )
    # Agar user pehle se registered hoga toh 400 ayega, warna naye user par 200 ya 201 aayega
    assert response.status_code in [200, 201, 400]


def test_login_user():
    """Login endpoint ko test karne ke liye form data use karein."""
    response = client.post(
        "/login",
        data={
            "username": "ahsan@test.com",  # OAuth2 form expects 'username'
            "password": "123456"
        }
    )
    assert response.status_code == 200

    def test_product_reduces_stock():
       
     """Test karta hai ke product ka stock sahi tarah reduce hota hai."""
    product = ProductModel(1, "Mouse", Decimal("20.00"), 5)
    product.reduce_stock(2)
    assert product.stock == 3

def test_product_rejects_overselling():
    """Test karta hai ke available stock se zyada quantity mangne par error aaye."""
    product = ProductModel(1, "Mouse", Decimal("20.00"), 2)
    with pytest.raises(ValueError, match="Insufficient stock"):
        product.reduce_stock(3)
    assert product.stock == 2

def test_order_cancellation_rules():
    """Test karta hai ke pending ya confirmed order cancel ho sakta hai aur status update hota hai."""
    keyboard = ProductModel(101, "Keyboard", Decimal("45.00"), 10)
    item = OrderItem(keyboard.id, keyboard.name, 2, keyboard.price)
    order = Order("ORD-1001", customer_id=7, items=[item])
    
    # Initial status pending hona chahiye
    assert order.status == "PENDING_PAYMENT"
    
    # Order cancel karein
    order.cancel()
    assert order.status == "CANCELLED"