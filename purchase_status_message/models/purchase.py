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

from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp

class purchase_order(osv.osv):
    _inherit = "purchase.order"

    def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
        return super(purchase_order, self)._amount_all(cr, uid, ids, field_name, arg, context)

    def _get_order(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('purchase.order.line').browse(cr, uid, ids, context=context):
            result[line.order_id.id] = True
        return result.keys()

    READONLY_STATES = {
        'confirmed': [('readonly', True)],
        'approved': [('readonly', True)],
        'done': [('readonly', True)]
    }

    _track = {
        'state': {
            'purchase_status_message.mt_rfq_draft': lambda self, cr, uid, obj, ctx=None: obj.state == 'draft',
            'purchase_status_message.mt_rfq_sent': lambda self, cr, uid, obj, ctx=None: obj.state == 'sent',
            'purchase_status_message.mt_rfq_bid': lambda self, cr, uid, obj, ctx=None: obj.state == 'bid',
            'purchase_status_message.mt_rfq_confirmed': lambda self, cr, uid, obj, ctx=None: obj.state == 'confirmed',
            'purchase_status_message.mt_rfq_approved': lambda self, cr, uid, obj, ctx=None: obj.state == 'approved',
            'purchase_status_message.mt_rfq_except_picking': lambda self, cr, uid, obj, ctx=None: obj.state == 'except_picking',
            'purchase_status_message.mt_rfq_except_invoice': lambda self, cr, uid, obj, ctx=None: obj.state == 'except_invoice',
            'purchase_status_message.mt_rfq_done': lambda self, cr, uid, obj, ctx=None: obj.state == 'done',
            'purchase_status_message.mt_rfq_cancel': lambda self, cr, uid, obj, ctx=None: obj.state == 'cancel',
        },
    }

    _columns = {
        'partner_id':fields.many2one('res.partner', 'Supplier', required=True, states=READONLY_STATES,
            change_default=True, track_visibility='false'), 
        'amount_untaxed': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Untaxed Amount',
            store={
                'purchase.order.line': (_get_order, None, 10),
            }, multi="sums", help="The amount without tax", track_visibility='false'),
    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

