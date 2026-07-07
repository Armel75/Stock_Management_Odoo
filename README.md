# 📦 Stock Management Odoo

> Enterprise-grade Odoo application for real-time stock and price consultation synchronized with Sage X3.

## Overview

This project is an Odoo module designed to provide a fast and reliable consultation of product inventories and prices across the organization.

Instead of querying the ERP directly for every request, the application maintains a dedicated PostgreSQL database synchronized daily with Sage X3. This architecture significantly improves performance while reducing the load on the ERP system.

The synchronization process is fully automated through scheduled Cron Jobs, ensuring that inventory levels and pricing data remain accurate and up to date.

---

## Business Features

- Product stock consultation
- Product price consultation
- Daily synchronization with Sage X3
- Automated Cron-based data import
- PostgreSQL optimized storage
- High-performance data retrieval
- Clean Odoo module architecture
- Scalable service-oriented design

---

## Technical Architecture

```text
                +----------------+
                |    Sage X3     |
                +--------+-------+
                         |
                  Daily Synchronization
                     (Odoo Cron)
                         |
                         ▼
                +----------------+
                | PostgreSQL DB  |
                +--------+-------+
                         |
                    Repository Layer
                         |
                    Service Layer
                         |
                     Odoo Models
                         |
                         ▼
                  Odoo User Interface
```

---

## Technologies

- Odoo
- Python
- PostgreSQL
- Cron Jobs
- Repository Pattern
- Service Layer
- ORM
- XML Views
- Git

---

## Project Goals

This project demonstrates the implementation of an enterprise integration between Odoo and Sage X3 while following software engineering best practices.

Key objectives include:

- Separation of concerns
- Maintainable architecture
- Database optimization
- Automated background processing
- Modular Odoo development
- Enterprise application design

---

## Skills Demonstrated

- Enterprise Software Development
- Odoo Custom Module Development
- PostgreSQL Database Design
- Python Backend Development
- ERP Integration
- Scheduled Automation
- Clean Architecture
- Performance Optimization
- Git Version Control

---

## Future Improvements

- Incremental synchronization
- REST API exposure
- Advanced search filters
- Stock movement history
- Dashboard & Analytics
- Docker deployment
- Unit and integration testing

---

## Author

Developed as part of an enterprise Odoo solution focused on inventory visibility, ERP integration and backend architecture.

<img width="1590" height="721" alt="image" src="https://github.com/user-attachments/assets/36f89367-d72e-495f-afb0-79f3f28f753e" />

