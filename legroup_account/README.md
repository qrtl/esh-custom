LeadExpress Group Account
=========================

This module makes following adjustments to group/security settings.

- Creates a new group "LeadExpress Accounting" (`legroup_account`), which only has read access to accounting models.
- Adjusts existing accounting group(s) so that accessible menu items are limited for users belonging to LeadExpress Accounting group (and not other accounting groups).


Installation
============

Just install the module.  No special steps are required.


Configuration
=============

Assign "LeadExpress Accounting" group to users on LeadExpress.


Usage
=====

Only following menu items should be visible and linked objects to them are read-only for "LeadExpress Accounting" group:

- 'Accounting > Suppliers > Supplier Invoices`
- 'Accounting > Suppliers > Supplier Payments`

User should still be able to send messages in invoices and vouchers by adding themselves as a follower.
