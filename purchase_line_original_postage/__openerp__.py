# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) Rooms For (Hong Kong) Limited T/A OSCG (<http://www.openerp-asia.net>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Purchase Order Line Original and Postage',
    'version': '8.0.1.0',
    'category': 'Purchase Management',
    'author': 'Rooms For (Hong Kong) Limited T/A OSCG',
    'summary': 'Add original and postage fields in Purchase Order and Invoice Lines',
    'description': """
* Adds Original fields of Unit Price, Quantity, Postage and Subtotal in Purchase Order and Invoice Lines
* Adds Postage fields in Purchase Order and Invoice Lines
* Adds a Negotiation Fee field in Invoice Line
* Adds above columns in the report of Invoice
* Adds Variation and Comments fields in Purchase Order Lines
    """,
    'depends': ["purchase", "account_invoice"], 
    'data': [
        'views/purchase_view.xml',
        'views/account_invoice_view.xml',
        'views/report_invoice.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}

