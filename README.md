DataBase Project - Automotive Service and Damage Tracking Database System
DataBase Project is a desktop database application built for a university database course. It models the operational flow of an automotive service business with two connected modules:

Car Repair Tracking: service entries, work orders, labor records, used parts, inventory, supplier orders, invoices, payments, and employee registration.
Damage Tracking: customers, vehicles, accident records, damage assessments, insurance policies, insurance claims, and parts inventory.
The project is intentionally database-centered: most screens perform CRUD operations against a normalized SQL Server schema and use joins to show business-friendly records in the Tkinter interface.

Tech Stack
Python
Tkinter
Microsoft SQL Server
pyodbc
SHA-256 based login hash comparison

Project Structure
DBProject/
  car_repair_app/        # Repair workflow UI screens
  damage_app/            # Damage and insurance workflow UI screens
  core/                  # Shared database connection and authentication
  utils/                 # Shared helper functions
  docs/                  # Database and workflow notes
  run_car_repair.py      # Car repair module launcher
  run_damage_tracking.py # Damage tracking module launcher
  
Key Database Areas
Personnel authentication and department/position based user records
Customer and vehicle ownership records
Service intake, repair work orders, labor, and used part tracking
Inventory stock updates through supplier orders and used parts
Invoice and payment lifecycle
Accident records, damage assessments, insurance policies, and claims

Setup
Create and activate a virtual environment.
python -m venv .venv
.venv\Scripts\activate
Install dependencies.
pip install -r requirements.txt
Configure SQL Server access.
Use .env.example as a template for local settings. The application reads these values from environment variables:

DB_DRIVER=SQL Server
DB_SERVER=localhost
DB_NAME=DBProject
DB_TRUSTED_CONNECTION=yes
If SQL Server authentication is used, set DB_TRUSTED_CONNECTION=no, DB_USER, and DB_PASSWORD.

Note: .env is ignored by Git. Export these values in your terminal or IDE run configuration before starting the app.

Make sure the SQL Server database is named DBProject or update DB_NAME.

Run one of the modules.

python run_car_repair.py
python run_damage_tracking.py
Notes for Reviewers
The application expects an existing SQL Server schema and seed data.
Passwords in the Personnel table are expected to be stored as SHA-256 hashes.
Database access is centralized in core/db.py, making it easy to change the server, database name, or authentication mode without editing every screen.


Course Project Focus
This repository demonstrates database design usage through a real business scenario: entities are connected across customers, 
vehicles, service operations, inventory, payments, personnel, accidents, assessments, and insurance records. The UI is simple by design, while the database interactions show the main value of the project.
