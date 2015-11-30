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
    'name': 'Purchase Order Line Postage',
    'version': '8.0.1.0',
    'category': 'Purchase Management',
    'author': 'Rooms For (Hong Kong) Limited T/A OSCG',
    'summary': 'Add a field of postage in Purchase Order Line',
    'description': """
* Adds a field of postage in Purchase Order Line
    """,
    'depends': ["purchase", "account"], 
    'data': [
        'views/purchase_view.xml',
        'views/account_invoice_view.xml',
        'views/report_invoice.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}

