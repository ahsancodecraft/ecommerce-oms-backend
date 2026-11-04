# 🚀 E-Commerce Order Management System (OMS) - Backend API

A practical, production-grade backend implementation of an E-Commerce Order Management System built using **Python**, **FastAPI**, **SQLAlchemy**, and **Object-Oriented Programming (OOP)** principles.

---

## 🌟 Project Overview & Features

This backend service handles core e-commerce workflows reliably while preventing common issues such as overselling, inconsistent pricing, and uncoordinated inventory changes.

* **📦 Product Catalog**: Manage products with strict validation on stock, pricing, and active status.
* **🔐 Secure Authentication & Authorization**: JWT-based user registration and login, ensuring customers can only access and modify their own orders.
* **🛒 Shopping Cart & Checkout**: Dynamic server-side price calculation using `Decimal`, inventory reservation, and simulated payment processing.
* **⚙️ Order Lifecycle & State Machine**: Explicit status transitions (`PENDING_PAYMENT` ➔ `CONFIRMED` / `CANCELLED`).
* **🔄 Reliable Cancellation Workflow**: Handle order cancellations and safe inventory restoration without duplicate restocks.
* **🧪 Automated Testing**: Comprehensive unit and integration test suite built with `pytest`.

---

## 🛠️ Technology Stack

* **Language**: Python 3.12+
* **Framework**: FastAPI
* **ORM & Database**: SQLAlchemy 2.x with SQLite / PostgreSQL
* **Validation**: Pydantic
* **Testing**: Pytest

---

## 📂 Project Architecture & OOP Design

The project strictly follows core Object-Oriented Design principles:

1. **Encapsulation**: Domain models (`Product`, `Order`) protect internal states (e.g., preventing negative stock or invalid price assignments through validated methods).
2. **Polymorphism & Abstraction**: Payment processing uses pluggable interfaces (`PaymentProcessor` protocol) allowing alternative providers like `FakePaymentProcessor`.
3. **Single Responsibility Principle (SRP)**: Separation of concerns across database models, domain logic, service layers, and API routes.
4. **Dependency Inversion**: Services depend on abstractions and injected database sessions.

---

## ⚙️ Installation & Setup Instructions

### 1. Clone & Navigate
Clone the repository or open the project folder in VS Code.

### 2. Create Virtual Environment
```bash
python -m venv venv
```
### On Vs-Code Terminal:
.\venv\Scripts\activate
``
### 3. Install Dependencies
```bash
python -m pip install fastapi uvicorn sqlalchemy pydantic pydantic-settings 
```
### 4. Initialize Database
```bash 
 python init_db.py
 ```
### 🚀 Running the Application
###    Start the development server using Uvicorn:
```bash
uvicorn main:app --reload
```
### 🚀 Running the Application

###  Start the development server using Uvicorn:
```bash
uvicorn main:app --reload
```
### Open your browser and explore the interactive Swagger UI documentation:
```go to
👉 http://127.0.0.1:8000/docs
```
### 🧪 Running TestsTo run the automated test suite and verify business rules:
```bash
pytest
```
### 📌 Main API Endpoints
``
### Method 	Endpoint	         Description	                       Access
```
 POST	       /register       Register a new customer      	        Public
 POST	      /login	       Authenticate and obtain JWT token	    Public
 GET	     /products	       List active catalog products	            Public
 POST	    /checkout          Submit cart items and place order	    Authenticated
 GET	   /orders/me	       Fetch logged-in user's order history	    Authenticated
 POST     /orders/{id}/cancel  Cancel Orders/Restore Inventory	        Authenticated

