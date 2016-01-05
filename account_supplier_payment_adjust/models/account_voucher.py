# -*- coding: utf-8 -*-
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 Rooms For (Hong Kong) Limited T/A OSCG
#    <https://www.odoo-asia.com>
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

from openerp.osv import fields, osv
from openerp.tools.translate import _

class account_voucher(osv.osv):
    _inherit = "account.voucher"

    def _get_currency_help_label(self, cr, uid, currency_id, payment_rate, payment_rate_currency_id, context=None):
        currency_help_label = _('You can see the exchange rate by clicking the above link.')
        return currency_help_label

class account_voucher_line(osv.osv):
    _inherit = "account.voucher.line"

    _columns = {
        'amount_currency': fields.related('move_line_id', 'amount_currency', type='float', relation='account.move.line', string='Amount Currency', readonly=1)
    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

