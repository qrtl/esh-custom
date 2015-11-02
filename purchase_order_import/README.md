Purchase Data Import
====================

This module provides following functions:

* Imports purchase data of designated format from `.csv` file (with UTF-8 encoding), and creates following transactions:
 * Purchase Order
 * Supplier Invoice
 * Supplier Payment
 
This module depends on `base_import_log` module.
 

Installation
============

* Place this module and `base_import_log` module in your addons directory, update the module list in Odoo, and install this module.  `base_import_log` module should be automatically installed when you install this module. 


Configuration
=============

* User should belong to 'Data Import' group.  Adjust the user access right settings from `Settings > Users > (the user) > Access Rights > Technical Settings`.
* Select default journals ('Invoice Journal' and 'Payment Journal') in "Purchase Import Defaults" screen.  The values are used to propose journals in "Purchase Data Import" wizard.
* Selece default 'Invoicing Control' in "Purchase Import Defaults" screen.  If select other than 'Based on generated draft invoice', cannot complete validation of invoices and payments. 


Usage
=====

Go to `Import > Import > Import Purchase Order` to import purchase data in `.csv` format.

Go to `Import > Data Import Log > Import Log` to find the import history / error log.


Program Logic
-------------

* The first line of the import file is field labels shown as follows:
 * 'Group'
 * 'Line Product'
 * 'Line Description'
 * 'Line Planned Date'
 * 'Line Unit Price'
 * 'Line Qty'
 * 'Line Tax'
 * 'Supplier'
 * 'Pricelist'
 * 'Warehouse'
 * 'Notes'
* Records for import should be prepared from the second line onwards.
* "Group" values should be used to separate purchase orders.
* Products are identified based on "Internal Reference" (`default_code`).
* Suppliers are identified based on "Name".
* Negative values are not allowed for "Unit Price" and "Qty" fields of the import file.
* Purchase order currency is determined based on the selected "Pricelist".
* If "Line Description" is left blank, the system proposes a description according to the standard logic (i.e. "Internal Reference" + "Name" of the product).
* If "Line Planned Date" is specified, the system proposes "Order Date" as the specified date.
* For document level fields (Supplier, Pricelist, Notes, Warehouse, etc.), the program only looks at the first record in the same "Group" and ignore the rest (there will be no error even if there is inconsistency - e.g. different Suppliers for the same PO).
* The program should not create any record if there is an error in any of the record.  User is expected to find the error content in the error log, correct all the errors in the import file, and re-import it.
