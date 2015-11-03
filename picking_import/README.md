Stock Data Import
====================

This module provides following functions:

* Imports picking data of designated format from `.csv` file, and processes following transactions:
 * Availability check on outgoing picking
 * Transfer picking

This module depends on `base_import_log` module.


Installation
============

* Place this module and `base_import_log` module in your addons directory, update the module list in Odoo, and install this module.  `base_import_log` module should be automatically installed when you install this module. 


Configuration
=============

* User should belong to 'Data Import' group.  Adjust the user access right settings from `Settings > Users > (the user) > Access Rights > Technical Settings`.


Usage
=====

Go to `Import > Import > Import Pickings` to import picking data in `.csv` format.

Go to `Import > Data Import Log > Import Log` to find the import history / error log.


Program Logic
-------------

* The first line of the import file is a field label 'Number'.  Records for import should be prepared from the second line onwards.
* "Number" values are identified based on "Order Number" of the purchase/sales orders.  Select "Puchase/Sales" as "Picking Type" in the "Import Pickings" wizard.
* The program should not create any record if there is an error in any of the records.  User is expected to find the error content in the error log, correct all the errors in the import file, and re-import it.
