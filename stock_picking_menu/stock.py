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


class stock_picking(osv.osv):
    _inherit = "stock.picking"

    def _default_picking_type_id(self, cr, uid, context=None):
        context = context or {}
        # following two lines may not be needed - default from window action
        # probably overrides the _defaults setting of picking_type_id
        if context.get('default_picking_type_id', False):
            return context['default_picking_type_id']
        else:
            PickingType = self.pool.get('stock.picking.type')
            if context.get('default_picking_type_code', False):
                return PickingType.search(cr, uid,
                    [('code','=',context['default_picking_type_code'])],
                    order='id')[0]
            else:
                return False

    _defaults = {
        'picking_type_id': _default_picking_type_id
    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
