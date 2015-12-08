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

class purchase_order(osv.osv):
    _inherit = "purchase.order"

    READONLY_STATES = {
        'confirmed': [('readonly', True)],
        'approved': [('readonly', True)],
        'done': [('readonly', True)]
    }

    _track = {
        'state': {
            'purchase_bid_received_message.mt_rfq_draft': lambda self, cr, uid, obj, ctx=None: obj.state == 'draft',
            'purchase_bid_received_message.mt_rfq_sent': lambda self, cr, uid, obj, ctx=None: obj.state == 'sent',
            'purchase_bid_received_message.mt_rfq_bid': lambda self, cr, uid, obj, ctx=None: obj.state == 'bid',
            'purchase_bid_received_message.mt_rfq_confirmed': lambda self, cr, uid, obj, ctx=None: obj.state == 'confirmed',
            'purchase_bid_received_message.mt_rfq_approved': lambda self, cr, uid, obj, ctx=None: obj.state == 'approved',
            'purchase_bid_received_message.mt_rfq_except_picking': lambda self, cr, uid, obj, ctx=None: obj.state == 'except_picking',
            'purchase_bid_received_message.mt_rfq_except_invoice': lambda self, cr, uid, obj, ctx=None: obj.state == 'except_invoice',
            'purchase_bid_received_message.mt_rfq_done': lambda self, cr, uid, obj, ctx=None: obj.state == 'done',
            'purchase_bid_received_message.mt_rfq_cancel': lambda self, cr, uid, obj, ctx=None: obj.state == 'cancel',
        },
    }

    _columns = {
        'partner_id':fields.many2one('res.partner', 'Supplier', required=True, states=READONLY_STATES,
            change_default=True, track_visibility='false'), 
    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

