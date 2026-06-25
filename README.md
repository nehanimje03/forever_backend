# 👗 ForeverBuy - Fashion E-Commerce Platform

A modern, scalable, and production-ready fashion e-commerce platform built to deliver a seamless online shopping experience for customers and powerful management tools for administrators.

ForeverBuy allows users to explore fashion collections, discover trending products, manage shopping carts, place orders, and track purchases through a secure and intuitive interface.

---

# ✨ Features

## 👤 Authentication & User Management

* User Registration and Login
* JWT Authentication
* Refresh Token Support
* Password Reset Functionality
* Profile Management
* Secure Session Management

## 👗 Product Management

* Product Listings
* Product Details
* Featured Products
* Best Sellers
* Latest Arrivals
* Product Search
* Dynamic Filtering
* Product Variants and Sizes

## 📂 Category Management

* Men Collection
* Women Collection
* Kids Collection
* Seasonal Collections
* Category-Based Product Browsing

## ❤️ Wishlist System

* Add Products to Wishlist
* Remove Products from Wishlist
* Persistent Wishlist Support

## 🛒 Shopping Cart

* Add to Cart
* Update Quantity
* Remove Products
* Cart Price Calculation
* Real-Time Cart Updates

## 📦 Order Management

* Place Orders
* Order History
* Order Tracking
* Order Cancellation
* Order Details

## 💳 Payment Integration

* Secure Checkout
* Multiple Payment Methods
* Payment Verification
* Transaction History

## 📧 Notifications

* Order Confirmation Emails
* Shipping Updates
* Delivery Notifications
* Promotional Notifications

## 👨‍💼 Admin Features

* Product Management
* Inventory Management
* Order Management
* Customer Management
* Sales Analytics
* Category Management

---

# 🛠 Technology Stack

* Python 3.12+
* Django 5.x
* Django REST Framework
* PostgreSQL
* JWT Authentication
* Redis (Optional)
* Celery (Optional)
* SMTP Email Service
* Pillow
* CORS Headers
* Git & GitHub
* Postman

---

# 🚀 Installation

## Clone Repository

```bash
git clone https://github.com/your-username/foreverbuy_backend.git
cd foreverbuy_backend
```

## Create Virtual Environment

```bash
python -m venv venv
```

## Activate Virtual Environment

### Windows

```bash
venv\Scripts\activate
```

### Linux / macOS

```bash
source venv/bin/activate
```

## Install Dependencies

```bash
pip install -r requirements.txt
```

## Configure Environment Variables

Create a `.env` file in the root directory:

```env
DEBUG=True

SECRET_KEY=your_secret_key

DB_NAME=foreverbuy_db
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432

EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password
```

## Apply Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

## Create Superuser

```bash
python manage.py createsuperuser
```

## Run Development Server

```bash
python manage.py runserver
```

Server will be available at:

```text
http://127.0.0.1:8000/
```

---

# 🔐 Authentication

ForeverBuy uses JWT Authentication.

Example Authorization Header:

```http
Authorization: Bearer <access_token>
```
---

# 🔒 Security Features

* JWT Authentication
* Password Hashing
* Role-Based Authorization
* Environment Variable Protection
* CORS Protection
* CSRF Protection

---

# 📈 Future Enhancements

* AI Product Recommendations
* Multi-Vendor Marketplace
* Live Order Tracking
* Loyalty Rewards Program
* Coupon and Discount Engine
* Push Notifications
* Multi-Currency Support
* Multi-Language Support

---

# 🚀 Deployment

Recommended production stack:

* Gunicorn
* Nginx
* PostgreSQL
* Redis
* Docker
* AWS / Render / DigitalOcean

---

# 🤝 Contributing

1. Fork the repository.
2. Create a feature branch.
3. Commit your changes.
4. Push your branch.
5. Create a Pull Request.

---

---

# 👨‍💻 Author

Developed using Django and Django REST Framework to power modern fashion commerce applications.

---

# 🌍 Vision

ForeverBuy aims to redefine online fashion shopping by combining speed, elegance, security, and scalability into a single seamless experience.

Our mission is to make fashion shopping smarter, faster, and more accessible for customers around the world.
