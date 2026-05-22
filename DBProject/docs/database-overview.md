# Database Overview

This document summarizes the database responsibilities used by the application. It is based on the SQL operations in the Python screens.

## Main Entity Groups

| Area | Tables used by the application |
| --- | --- |
| Personnel and auth | `Personnel`, `Position`, `Department` |
| Customer and vehicle data | `Customer`, `Vehicle`, `VehicleModel` |
| Repair workflow | `ServiceEntry`, `RepairWorkOrder`, `LaborRecord`, `LaborRate`, `ServiceOperation`, `UsedPart` |
| Inventory and suppliers | `Inventory`, `Supplier`, `SupplierOrder` |
| Billing | `Invoice`, `Payment` |
| Damage workflow | `AccidentRecord`, `DamageAssessment`, `DamageDetail` |
| Insurance | `InsuranceCompany`, `InsurancePolicy`, `InsuranceClaim` |

## Workflow Summary

1. A personnel user logs in with email and password.
2. Customer and vehicle records are created or selected.
3. In the repair module, a vehicle enters service through `ServiceEntry`.
4. Repair work is tracked with `RepairWorkOrder`, `LaborRecord`, and `UsedPart`.
5. Inventory changes through supplier orders and used parts usage.
6. Completed service work can be invoiced and marked paid through `Payment`.
7. In the damage module, accidents are recorded for vehicles.
8. Damage assessments and damage details are linked to accident records.
9. Insurance policies and claims are managed around assessed damage.

## Database Features Demonstrated

- CRUD operations across multiple business domains
- Foreign-key style relationships between customers, vehicles, service entries, work orders, invoices, accidents, and claims
- Join-heavy list screens for readable operational views
- Aggregate dashboard queries for total vehicles, active repairs, and completed paid services
- Password hash comparison during login

## Suggested ERD Direction

For a GitHub screenshot or report, an ERD can highlight these central relationships:

```text
Customer -> Vehicle -> ServiceEntry -> RepairWorkOrder -> LaborRecord
                                      -> UsedPart -> Inventory
ServiceEntry -> Invoice -> Payment

Vehicle -> AccidentRecord -> DamageAssessment -> DamageDetail
Vehicle -> InsurancePolicy -> InsuranceClaim
Personnel -> ServiceEntry / RepairWorkOrder / LaborRecord
```
