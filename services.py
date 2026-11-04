from decimal import Decimal
from models import Cart, Order as OrderModel, OrderItem, ProductModel
from payment import DiscountPolicy, NoDiscountPolicy, PaymentProcessor
from sqlalchemy.orm import Session


class InventoryService:
  """Manages product stock availability using database sessions."""

  def __init__(self, db: Session):
    self.db = db

  def reserve_stock(self, cart: Cart) -> None:
    """Checks stock and safely reduces it in the database."""
    for product_id, item in cart.items.items():
      product = self.db.query(ProductModel).filter(ProductModel.id == product_id).first()
      if not product or not product.active:
        raise ValueError(f"Product ID {product_id} is inactive or does not exist.")
      if product.stock < item.quantity:
        raise ValueError(f"Insufficient stock available for {product.name}.")

    # Stock reduce karna aur database mein commit karna
    for product_id, item in cart.items.items():
      product = self.db.query(ProductModel).filter(ProductModel.id == product_id).first()
      product.reduce_stock(item.quantity)
    
    self.db.commit()

class OrderService:
  """Orchestrates checkout flow with database persistence."""

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
    """Executes complete checkout workflow."""
 

    if not cart.items:
      raise ValueError("Cannot checkout an empty cart.")

    # 1. Order items prepare karna
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

    # 2. Inventory check & stock reservation
    self.inventory_service.reserve_stock(cart)

    # 3. Discount calculation
    subtotal = order.total
    discount = self.discount_policy.calculate_discount(subtotal)
    final_amount = subtotal - discount

    try:
      # 4. Payment process karna
      payment_ref = self.payment_processor.charge(
          final_amount, idempotency_key=order.id
      )

      # 5. Order confirm karna
      order.confirm()
      print(f"Checkout Successful! Payment Reference: {payment_ref}")
      return order

    except Exception as e:
      # Payment fail hone par stock wapas restore karna
      order.mark_payment_failed()
      for item in order.items:
        product = self.db.query(ProductModel).filter(ProductModel.id == item.product_id).first()
        if product:
          product.restock(item.quantity)
      self.db.commit()
      raise RuntimeError(f"Checkout failed due to payment error: {e}")
