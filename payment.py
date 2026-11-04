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