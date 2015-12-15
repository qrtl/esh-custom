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

    def _amount_all_original(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        cur_obj=self.pool.get('res.currency')
        line_obj = self.pool['purchase.order.line']
        for order in self.browse(cr, uid, ids, context=context):
            res[order.id] = {
                'amount_untaxed': 0.0,
                'amount_tax': 0.0,
                'amount_total': 0.0,
                'amount_untaxed_original': 0.0,
                'amount_tax_original': 0.0,
                'amount_total_original': 0.0,
            }
            val = val1 = 0.0
            val_org = val1_org = 0.0
            cur = order.pricelist_id.currency_id
            for line in order.order_line:
                val1 += line.price_subtotal
                val1_org += line.price_subtotal_original
                line_price = line_obj._calc_line_base_price(cr, uid, line,
                                                            context=context)
                line_qty = line_obj._calc_line_quantity(cr, uid, line,
                                                        context=context)
                line_price_org = line_obj._calc_line_base_price_original(cr, uid, line,
                                                            context=context)
                line_qty_org = line_obj._calc_line_quantity_original(cr, uid, line,
                                                        context=context)
                for c in self.pool['account.tax'].compute_all(
                        cr, uid, line.taxes_id, line_price, line_qty,
                        line.product_id, order.partner_id)['taxes']:
                    val += c.get('amount', 0.0)
                for corg in self.pool['account.tax'].compute_all(
                        cr, uid, line.taxes_id, line_price_org, line_qty_org,
                        line.product_id, order.partner_id)['taxes']:
                    val_org += corg.get('amount', 0.0)
            res[order.id]['amount_tax']=cur_obj.round(cr, uid, cur, val)
            res[order.id]['amount_untaxed']=cur_obj.round(cr, uid, cur, val1)
            res[order.id]['amount_total']=res[order.id]['amount_untaxed'] + res[order.id]['amount_tax']
            res[order.id]['amount_tax_original']=cur_obj.round(cr, uid, cur, val_org)
            res[order.id]['amount_untaxed_original']=cur_obj.round(cr, uid, cur, val1_org)
            res[order.id]['amount_total_original']=res[order.id]['amount_untaxed_original'] + res[order.id]['amount_tax_original']
        return res

    def _get_order(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('purchase.order.line').browse(cr, uid, ids, context=context):
            result[line.order_id.id] = True
        return result.keys()

    _columns = {
        'amount_untaxed': fields.function(_amount_all_original, digits_compute=dp.get_precision('Account'), string=_('Untaxed Amount'),
            store={
                'purchase.order.line': (_get_order, None, 10),
            }, multi="sums", help="The amount without tax", track_visibility='false'),
        'amount_tax': fields.function(_amount_all_original, digits_compute=dp.get_precision('Account'), string=_('Taxes'),
            store={
                'purchase.order.line': (_get_order, None, 10),
            }, multi="sums", help="The tax amount"),
        'amount_total': fields.function(_amount_all_original, digits_compute=dp.get_precision('Account'), string=_('Total'),
            store={
                'purchase.order.line': (_get_order, None, 10),
            }, multi="sums", help="The total amount"),
        'amount_untaxed_original': fields.function(_amount_all_original, digits_compute=dp.get_precision('Account'), string=_('Untaxed Amount (Original)'),
            store={
                'purchase.order.line': (_get_order, None, 10),
            }, multi="sums"),
        'amount_tax_original': fields.function(_amount_all_original, digits_compute=dp.get_precision('Account'), string=_('Taxes (Original)'),
            store={
                'purchase.order.line': (_get_order, None, 10),
            }, multi="sums"),
        'amount_total_original': fields.function(_amount_all_original, digits_compute=dp.get_precision('Account'), string=_('Total (Original)'),
            store={
                'purchase.order.line': (_get_order, None, 10),
            }, multi="sums"),
    }

    def _prepare_inv_line(self, cr, uid, account_id, order_line, context=None):
        res = super(purchase_order, self)._prepare_inv_line(cr, uid, account_id, order_line, context)
        res.update({'quantity_original': order_line.product_qty_original})
        res.update({'price_unit_original': order_line.price_unit_original})
        res.update({'postage_original': order_line.postage_original})
        res.update({'postage': order_line.postage})
        return res


class purchase_order_line(osv.osv):
    _inherit = "purchase.order.line"

    def _calc_line_base_price(self, cr, uid, line, context=None):
        """Return the base price of the line to be used for tax calculation.

        This function can be extended by other modules to modify this base
        price (adding a discount, for example).
        """
        return line.price_unit

    def _calc_line_quantity(self, cr, uid, line, context=None):
        """Return the base quantity of the line to be used for the subtotal.

        This function can be extended by other modules to modify this base
        quantity (adding for example offers 3x2 and so on).
        """
        return line.product_qty

    def _calc_line_base_price_original(self, cr, uid, line, context=None):
        """Return the base price of the line to be used for tax calculation.

        This function can be extended by other modules to modify this base
        price (adding a discount, for example).
        """
        return line.price_unit_original

    def _calc_line_quantity_original(self, cr, uid, line, context=None):
        """Return the base quantity of the line to be used for the subtotal.

        This function can be extended by other modules to modify this base
        quantity (adding for example offers 3x2 and so on).
        """
        return line.product_qty_original

    def _calc_line_postage_original(self, cr, uid, line, context=None):
        return line.postage_original

    def _amount_line_original(self, cr, uid, ids, prop, arg, context=None):
        res = {}
        cur_obj = self.pool.get('res.currency')
        tax_obj = self.pool.get('account.tax')
        for line in self.browse(cr, uid, ids, context=context):
            line_price = self._calc_line_base_price_original(cr, uid, line,
                                                    context=context)
            line_qty = self._calc_line_quantity_original(cr, uid, line,
                                                context=context)
            line_postage = self._calc_line_postage_original(cr, uid, line,
                                                context=context)
            taxes = tax_obj.compute_all(cr, uid, line.taxes_id, line_price,
                                        line_qty, line.product_id,
                                        line.order_id.partner_id)
            line_total = taxes['total']
            line_total += line_postage
            cur = line.order_id.pricelist_id.currency_id
            res[line.id] = cur_obj.round(cr, uid, cur, line_total)
        return res

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
        'name': fields.text(_('Description'), required=True),
        'product_id': fields.many2one('product.product', _('Product'), domain=[('purchase_ok','=',True)], change_default=True),
        'variation': fields.text(_('Variation')),
        'advice': fields.text(_('Comments')),
        'product_qty_original': fields.float(_('Quantity (Original)'), digits_compute=dp.get_precision('Product Unit of Measure')),
        'price_unit_original': fields.float(_('Unit Price (Original)'), digits_compute= dp.get_precision('Product Price')),
        'postage_original': fields.float(_('Postage (Original)'), digits_compute= dp.get_precision('Product Price')),
        'price_subtotal_original': fields.function(_amount_line_original, string=_('Subtotal (Original)'), digits_compute= dp.get_precision('Account')),
        'postage': fields.float(_('Postage'), digits_compute=dp.get_precision('Product Price')),
        'price_subtotal': fields.function(_amount_line_postage, string=_('Subtotal'), digits_compute= dp.get_precision('Account')),
    }
    _defaults = {
        'product_qty_original': lambda *a: 1.0,
        'postage_original': lambda *a: 0.0,
        'postage': lambda *a: 0.0,
    }

    def onchange_product_id_original(self, cr, uid, ids, pricelist_id, product_id, qty, uom_id,
            partner_id, date_order=False, fiscal_position_id=False, date_planned=False,
            name=False, price_unit=False, state='draft', context=None):

        res = self.onchange_product_id(cr, uid, ids, pricelist_id, product_id, qty, uom_id,
            partner_id, date_order, fiscal_position_id, date_planned,
            name, price_unit, state, context)

        qty_org = self.onchange_product_id(cr, uid, ids, pricelist_id, product_id, qty, uom_id,
            partner_id, date_order, fiscal_position_id, date_planned,
            name, price_unit, state, context)['value'].get('product_qty')

        price_unit_org = self.onchange_product_id(cr, uid, ids, pricelist_id, product_id, qty, uom_id,
            partner_id, date_order, fiscal_position_id, date_planned,
            name, price_unit, state, context)['value'].get('price_unit')

        res['value'].update({'product_qty_original': qty_org, 'price_unit_original': price_unit_org})

        return res


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
