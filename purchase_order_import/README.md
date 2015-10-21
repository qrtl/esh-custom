Purchase Data Import
====================

This module provides following functions:

* Imports purchase data of designated format from `.xlsx` file, and creates following transactions:
 * Purchase order
 * Supplier invoice
 * Supplier payment
 
This module depends on `base_import_log` module.
 

Installation
============

* Install `python-xlrd` in the Odoo server before installing the module.
* Place this module and `base_import_log` module in your addons directory, update the module list in Odoo, and install this module.  `base_import_log` module should be automatically installed when you install this module. 


Configuration
=============

* User should belong to 'Data Import' group.  Adjust the user access right settings as necessary.
* Select default journals (invoice journal and payment journal) in "Purchase Import Defaults" screen.  The values are used to propose journals in "Purchase Data Import" wizard.


Usage
=====

Go to `Import > Import > Import Purchase Order` to import purchase data in `.xlsx` format.

Go to `Import > Data Import Log > Import Log` to find the import history / error log.


Program Logic
-------------

* The first line of the import file is field labels.  Records for import should prepared from the second line onwards.
* "Group" values should be used to separate purchase orders.
* Products are identified based on "Internal Reference" (`default_code`).
* Suppliers are identified based on "Name".
* Negative values are not allowed for "Unit Price" and "Qty" fields of the import file.
* Purchase order currency is determined based on the selected "Pricelist".
* If "Line Description" is left blank, the system proposes a description according to the standard logic (i.e. "Internal Reference" + "Name" of the product).
* For document level fields (Supplier, Pricelist, Notes, Warehouse, etc.), the program only looks at the first record in the same "Group" and ignore the rest (there will be no error even if there is inconsistency - e.g. different Suppliers for the same PO).
* The program should not create any record if there is an error in any of the record.  User is expected to find the error content in the error log, correct all the errors in the import file, and re-import it.
