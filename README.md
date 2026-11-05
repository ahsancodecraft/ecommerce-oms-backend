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

## 🛠️ Technology Stack & Logos

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

1. **Encapsulation**: Domain models (`Product`, `Order`) protect internal states and prevent invalid assignments (e.g., negative stock or zero pricing) through validated methods[cite: 29].
2. **Polymorphism & Abstraction**: Payment processing uses pluggable protocols (`PaymentProcessor` protocol) allowing alternative providers like `FakePaymentProcessor`[cite: 30].
3. **Single Responsibility Principle (SRP)**: Separation of concerns across database models, domain logic, service layers, and API routes[cite: 31].
4. **Dependency Inversion**: High-level services depend on abstractions and injected database sessions rather than concrete low-level details[cite: 31].

---

## 🔄 Order Lifecycle & State Rules

The system implements explicit state machine transitions to maintain consistency:

* `PENDING_PAYMENT` ➔ `CONFIRMED` (Payment verified successful)[cite: 31, 32]
* `PENDING_PAYMENT` ➔ `PAYMENT_FAILED` (Payment definitively failed)
* `PENDING_PAYMENT` ➔ `CANCELLED` (Cancellation allowed, reservation released)
* `CONFIRMED` ➔ `CANCELLED` (Policy allowed; coordinates refund and inventory restoration)[cite: 32]

---

## ⚙️ Installation & Setup Instructions

### 1. Clone & Navigate
Clone the repository or open the project folder in VS Code[cite: 32].

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