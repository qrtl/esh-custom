# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) Rooms For (Hong Kong) Limited T/A OSCG
#    <http://www.openerp-asia.net>
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

from openerp import _
import openerp.addons.decimal_precision as dp
from openerp.osv import fields, osv


class purchase_order(osv.osv):
    _inherit = "purchase.order"

    def _prepare_inv_line(self, cr, uid, account_id, order_line, context=None):
        res = super(purchase_order, self)._prepare_inv_line(cr, uid, account_id, order_line, context)
        res.update({'postage': order_line.postage})
        return res


class purchase_order_line(osv.osv):
    _inherit = "purchase.order.line"

    def _calc_line_postage(self, cr, uid, line, context=None):
        return line.postage

    def _amount_line_postage(self, cr, uid, ids, prop, arg, context=None):
        res = {}
        cur_obj = self.pool.get('res.currency')
        tax_obj = self.pool.get('account.tax')
        for line in self.browse(cr, uid, ids, context=context):
            line_price = self._calc_line_base_price(cr, uid, line,
                                                    context=context)
            line_qty = self._calc_line_quantity(cr, uid, line,
                                                context=context)
            line_postage = self._calc_line_postage(cr, uid, line,
                                                context=context)
            taxes = tax_obj.compute_all(cr, uid, line.taxes_id, line_price,
                                        line_qty, line.product_id,
                                        line.order_id.partner_id)
            line_total = taxes['total']
            line_total += line_postage
            cur = line.order_id.pricelist_id.currency_id
            res[line.id] = cur_obj.round(cr, uid, cur, line_total)
        return res

    _columns = {
        'postage': fields.float(_('Postage'), digits_compute=dp.get_precision('Product Price')),
        'price_subtotal': fields.function(_amount_line_postage, string='Subtotal', digits_compute= dp.get_precision('Account')),
    }
    _defaults = {
        'postage': lambda *a: 0.0,
    }


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
