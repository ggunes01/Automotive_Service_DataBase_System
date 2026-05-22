# Automotive Service & Damage Tracking Database System

A desktop-based database application developed for a university database systems course.  
The project simulates the operational workflow of an automotive service business through two integrated modules:

- **Car Repair Tracking System**
- **Damage & Insurance Tracking System**

The project is primarily **database-centered** and focuses on demonstrating relational database design, SQL operations, and business process modeling using Microsoft SQL Server.


# Features

## Car Repair Tracking Module

- Service intake and repair tracking
- Work order management
- Labor and technician records
- Used parts tracking
- Inventory management
- Supplier order management
- Invoice generation
- Payment tracking
- Personnel registration and authentication


## Damage & Insurance Tracking Module

- Customer and vehicle management
- Accident record tracking
- Damage assessment records
- Insurance policy management
- Insurance claim tracking
- Related parts and inventory records



# Technologies Used

- **Python**
- **Tkinter** (Desktop GUI)
- **Microsoft SQL Server**
- **pyodbc**
- **SHA-256 password hash verification**



# Project Structure

```text
DBProject/
│
├── car_repair_app/          # Car repair workflow screens
├── damage_app/              # Damage & insurance workflow screens
├── core/                    # Shared database connection & authentication
├── utils/                   # Helper utilities
│
├── docs/                    # Database notes and documentation
│
├── run_car_repair.py        # Launch car repair module
├── run_damage_tracking.py   # Launch damage tracking module
│
└── requirements.txt

# Database Scope

The system includes relational structures for:

- Personnel authentication and authorization
- Department and position-based employee records
- Customer and vehicle ownership information
- Service intake and repair operations
- Labor and used-part tracking
- Supplier orders and stock management
- Invoice and payment lifecycle
- Accident and damage assessment records
- Insurance policies and claim management

The application uses SQL joins extensively to present business-friendly records inside the Tkinter interface.



# Setup

## 1. Create a Virtual Environment

```bash
python -m venv .venv


Activate the environment:

### Windows

```bash
.venv\Scripts\activate
```


## 2. Install Dependencies

```bash
pip install -r requirements.txt
```



## 3. Configure SQL Server Connection

Use the following environment variables:

```env
DB_DRIVER=SQL Server
DB_SERVER=localhost
DB_NAME=DBProject
DB_TRUSTED_CONNECTION=yes
```

If using SQL Server Authentication:

```env
DB_TRUSTED_CONNECTION=no
DB_USER=your_username
DB_PASSWORD=your_password
```

> `.env` files are ignored by Git for security reasons.



## 4. Prepare the Database

Make sure:

- SQL Server is running
- The database name is `DBProject`
- Required tables and seed data already exist



## 5. Run the Application

### Car Repair Module

```bash
python run_car_repair.py
```

### Damage Tracking Module

```bash
python run_damage_tracking.py
```

---

# Authentication

Personnel passwords are expected to be stored using **SHA-256 hashing** inside the database.



This makes database configuration and authentication management easier to maintain.


# Educational Purpose

This project was developed as a university course project to demonstrate:

- Relational database design
- SQL-based CRUD operations
- Entity relationships
- Normalization principles
- Real-world business workflow modeling
- Database-driven desktop application development

The user interface is intentionally lightweight, while the main focus is placed on database structure, relationships, and data operations.


