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

from openerp import models, fields, api, _
import openerp.addons.decimal_precision as dp

class account_invoice_line(models.Model):
    _inherit = "account.invoice.line"

    @api.one
    @api.depends('price_unit', 'discount', 'invoice_line_tax_id', 'quantity',
        'product_id', 'invoice_id.partner_id', 'invoice_id.currency_id', 'postage')
    def _compute_price_postage(self):
        price = self.price_unit * (1 - (self.discount or 0.0) / 100.0)
        taxes = self.invoice_line_tax_id.compute_all(price, self.quantity, product=self.product_id, partner=self.invoice_id.partner_id)
        self.price_subtotal = taxes['total']
        self.price_subtotal += self.postage
        if self.invoice_id:
            self.price_subtotal = self.invoice_id.currency_id.round(self.price_subtotal)

    @api.one
    @api.depends('price_unit_original', 'discount', 'invoice_line_tax_id', 'quantity_original',
        'product_id', 'invoice_id.partner_id', 'invoice_id.currency_id', 'postage_original')
    def _compute_price_original(self):
        price = self.price_unit_original * (1 - (self.discount or 0.0) / 100.0)
        taxes = self.invoice_line_tax_id.compute_all(price, self.quantity_original, product=self.product_id, partner=self.invoice_id.partner_id)
        self.price_subtotal_original = taxes['total']
        self.price_subtotal_original += self.postage_original
        if self.invoice_id:
            self.price_subtotal_original = self.invoice_id.currency_id.round(self.price_subtotal_original)

    @api.one
    @api.depends('price_unit', 'price_unit_original', 'invoice_line_tax_id', 'quantity',
        'product_id', 'invoice_id.partner_id', 'invoice_id.currency_id', 'postage', 'postage_original')
    def _compute_negotiate_fee(self):
        price = (self.price_unit_original - self.price_unit) + (self.postage_original - self.postage)
        taxes = self.invoice_line_tax_id.compute_all(price, self.quantity, product=self.product_id, partner=self.invoice_id.partner_id)
        self.negotiate_fee = taxes['total'] * 0.1
        if self.invoice_id:
            self.negotiate_fee = self.invoice_id.currency_id.round(self.negotiate_fee)

    @api.model
    def _default_price_unit_original(self):
        if not self._context.get('check_total'):
            return 0
        total = self._context['check_total']
        for l in self._context.get('invoice_line', []):
            if isinstance(l, (list, tuple)) and len(l) >= 3 and l[2]:
                vals = l[2]
                price = vals.get('price_unit_original', 0) * (1 - vals.get('discount', 0) / 100.0)
                total = total - (price * vals.get('quantity_original'))
                taxes = vals.get('invoice_line_tax_id')
                if taxes and len(taxes[0]) >= 3 and taxes[0][2]:
                    taxes = self.env['account.tax'].browse(taxes[0][2])
                    tax_res = taxes.compute_all(price, vals.get('quantity_original'),
                        product=vals.get('product_id'), partner=self._context.get('partner_id'))
                    for tax in tax_res['taxes']:
                        total = total - tax['amount']
        return total


    name = fields.Text(string=_('Description'), required=True)
    product_id = fields.Many2one('product.product', string=_('Product'),
        ondelete='restrict', index=True)

    price_unit_original = fields.Float(string=_('Unit Price (Original)'), required=True,
        digits= dp.get_precision('Product Price'),
        default=_default_price_unit_original)
    quantity_original = fields.Float(string=_('Quantity (Original)'), digits= dp.get_precision('Product Unit of Measure'),
        required=True, default=1)
    postage_original = fields.Float(string=_('Postage (Original)'), digits= dp.get_precision('Product Price'))
    price_subtotal_original = fields.Float(string=_('Amount (Original)'), digits= dp.get_precision('Account'),
        store=True, readonly=True, compute='_compute_price_original')

    postage = fields.Float(string=_('Postage'), digits= dp.get_precision('Product Price'))
    price_subtotal = fields.Float(string=_('Amount'), digits= dp.get_precision('Account'),
        store=True, readonly=True, compute='_compute_price_postage')

    negotiate_fee = fields.Float(string=_('Negotiation Fee'), digits= dp.get_precision('Account'),
        store=True, readonly=True, compute='_compute_negotiate_fee')


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
