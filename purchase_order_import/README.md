Purchase Data Import
====================

This module provides following functions:

* Imports purchase data of designated format from .xlsx file, and creates following transactions:
 * Purchase order
 * Supplier invoice
 * Supplier payment
 
This module depends on `base_import_log` module.
 

Installation
============

* Install `python-xlrd` in the Odoo server before installing the module.


Configuration
=============

* User should belong to 'Data Import' group.  Adjust the user access right settings as necessary.
* Select default journals (invoice journal and payment journal) in "Purchase Import Defaults" screen.  The values are used to propose journals in "Purchase Data Import" wizard.


Usage
=====

Go to `Import > Import > Import Purchase Order` to import purchase data.

Go to `Import > Data Import Log > Import Log` to find the import history / error log.


Import Logic
------------

* `Group` values should be used to separate purchase orders.
* Products are identified based on Internal Reference (`default_code`).
* Purchase order currency is determined based on the selected Pricelist
* If `Line Description` is left blank, let the system propose the description according to the standard logic.
* 