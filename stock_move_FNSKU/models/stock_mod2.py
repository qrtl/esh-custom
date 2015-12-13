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

from datetime import date, datetime
from dateutil import relativedelta

from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT


class stock_move(osv.osv):
    _inherit = "stock.move"

    _columns = {
        'amazon_fnsku': fields.char('FNSKU'),
        'product_default_code': fields.related('product_id', 'default_code', type='char', string=_("Internal Reference")),
        'product_name': fields.related('product_id', 'name', type='char', string=_("Product Name")),
    }


class stock_location_path(osv.osv):
    _inherit = "stock.location.path"

    def _prepare_push_apply(self, cr, uid, rule, move, context=None):
        newdate = (datetime.strptime(move.date_expected, DEFAULT_SERVER_DATETIME_FORMAT) + relativedelta.relativedelta(days=rule.delay or 0)).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        return {
                'origin': move.origin or move.picking_id.name or "/",
                'location_id': move.location_dest_id.id,
                'location_dest_id': rule.location_dest_id.id,
                'date': newdate,
                'company_id': rule.company_id and rule.company_id.id or False,
                'date_expected': newdate,
                'picking_id': False,
                'picking_type_id': rule.picking_type_id and rule.picking_type_id.id or False,
                'propagate': rule.propagate,
                'push_rule_id': rule.id,
                'warehouse_id': rule.warehouse_id and rule.warehouse_id.id or False,
                'amazon_fnsku': move.amazon_fnsku,
            }


class stock_pack_operation(osv.osv):
    _inherit = "stock.pack.operation"

    _columns = {
        'amazon_fnsku': fields.char('FNSKU'),
    }


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
