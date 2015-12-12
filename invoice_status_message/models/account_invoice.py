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

from openerp import models, fields, api
import openerp.addons.decimal_precision as dp

class account_invoice(models.Model):
    _inherit = "account.invoice"

    _track = {
        'state': {
            'invoice_status_message.mt_invoice_draft': lambda self, cr, uid, obj, ctx=None: obj.state == 'draft' and obj.type in ('in_invoice', 'in_refund'),
            'invoice_status_message.mt_invoice_proforma': lambda self, cr, uid, obj, ctx=None: obj.state == 'proforma' and obj.type in ('in_invoice', 'in_refund'),
            'invoice_status_message.mt_invoice_paid': lambda self, cr, uid, obj, ctx=None: obj.state == 'paid' and obj.type in ('in_invoice', 'in_refund'),
            'invoice_status_message.mt_invoice_open': lambda self, cr, uid, obj, ctx=None: obj.state == 'open' and obj.type in ('in_invoice', 'in_refund'),
            'invoice_status_message.mt_invoice_cancel': lambda self, cr, uid, obj, ctx=None: obj.state == 'cancel' and obj.type in ('in_invoice', 'in_refund'),
        },
    }

    @api.model
    def _default_currency(self):
        journal = self._default_journal()
        return journal.currency or journal.company_id.currency_id

    type = fields.Selection([
            ('out_invoice','Customer Invoice'),
            ('in_invoice','Supplier Invoice'),
            ('out_refund','Customer Refund'),
            ('in_refund','Supplier Refund'),
        ], string='Type', readonly=True, index=True, change_default=True,
        default=lambda self: self._context.get('type', 'out_invoice'),
        track_visibility='false')
    state = fields.Selection([
            ('draft','Draft'),
            ('proforma','Pro-forma'),
            ('proforma2','Pro-forma'),
            ('open','Open'),
            ('paid','Paid'),
            ('cancel','Cancelled'),
        ], string='Status', index=True, readonly=True, default='draft',
        track_visibility='false', copy=False,
        help=" * The 'Draft' status is used when a user is encoding a new and unconfirmed Invoice.\n"
             " * The 'Pro-forma' when invoice is in Pro-forma status,invoice does not have an invoice number.\n"
             " * The 'Open' status is used when user create invoice,a invoice number is generated.Its in open status till user does not pay invoice.\n"
             " * The 'Paid' status is set automatically when the invoice is paid. Its related journal entries may or may not be reconciled.\n"
             " * The 'Cancelled' status is used when user cancel invoice.")
    partner_id = fields.Many2one('res.partner', string='Partner', change_default=True,
        required=True, readonly=True, states={'draft': [('readonly', False)]},
        track_visibility='false')
    amount_untaxed = fields.Float(string='Subtotal', digits=dp.get_precision('Account'),
        store=True, readonly=True, compute='_compute_amount', track_visibility='false')
    currency_id = fields.Many2one('res.currency', string='Currency',
        required=True, readonly=True, states={'draft': [('readonly', False)]},
        default=_default_currency, track_visibility='false')
    user_id = fields.Many2one('res.users', string='Salesperson', track_visibility='false',
        readonly=True, states={'draft': [('readonly', False)]},
        default=lambda self: self.env.user)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

