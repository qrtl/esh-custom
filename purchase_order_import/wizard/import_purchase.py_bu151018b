# -*- coding: utf-8 -*-
#    OpenERP, Open Source Management Solution
#    Copyright (c) Rooms For (Hong Kong) Limited T/A OSCG. All Rights Reserved.
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

from openerp import models, fields, api, _
from datetime import datetime
import base64
import xlrd
import sys
from openerp.exceptions import except_orm, Warning, RedirectWarning


class import_purchase(models.TransientModel):
    _name = 'import.purchase'
    
    @api.multi
    def _get_supplier_invoice_journal_id(self):
        return self.env.user.company_id.supplier_invoice_journal_id and self.env.user.company_id.supplier_invoice_journal_id.id or False
    
    @api.multi
    def _get_supplier_payment_journal_id(self):
        return self.env.user.company_id.supplier_payment_journal_id and self.env.user.company_id.supplier_payment_journal_id.id or False
    
    input_file = fields.Binary('Purchase Order File (.xlsx format)', required=True)
    datas_fname = fields.Char('File Path')
    supplier_invoice_journal_id = fields.Many2one('account.journal', string='Supplier Invoice Journal', default=_get_supplier_invoice_journal_id)
    supplier_payment_journal_id = fields.Many2one('account.journal', string='Supplier Payment Journal', default=_get_supplier_payment_journal_id)
    
    @api.multi
    def import_purchase_data(self):
        invoice_method_dict = {'Based on Purchase Order lines' : 'manual',
                              'Based on generated draft invoice' : 'order',
                              'Based on incoming shipments' : 'picking'}
        if not self.supplier_invoice_journal_id:
            raise Warning(_('Error!'),_('Please select Supplier Invoice Journal.'))
        
        if not self.supplier_payment_journal_id:
            raise Warning(_('Error!'),_('Please select Supplier Payment Journal.'))
        
        for line in self:
            try:
                lines = xlrd.open_workbook(file_contents=base64.decodestring(self.input_file))
            except IOError as e:
                raise Warning(_('Import Error!'),_(e.strerror))
            except ValueError as e:
                raise Warning(_('Import Error!'),_(e.strerror))
            except:
                e = sys.exc_info()[0]
                raise Warning(_('Import Error!'),_('Wrong file format. Please enter .xlsx file.'))
            if len(lines.sheet_names()) > 1:
                raise Warning(_('Import Error!'),_('Please check your xlsx file, it seems it contains more than one sheet.'))

            model = self.env['ir.model'].search([('model', '=', 'purchase.order')])

            product_dict = {}
            partner_dict = {}
            pricelist_dict = {}
            order_item_dict = {}
            tax_dict = {}
            order_dict = {}
            picking_dict = {}
            error_log_id = False
            
            ir_attachment = self.env['ir.attachment'].create({'name': self.datas_fname,
                        'datas': self.input_file,
                        'datas_fname': self.datas_fname})
            
            for sheet_name in lines.sheet_names(): 
                sheet = lines.sheet_by_name(sheet_name) 
                rows = sheet.nrows
                columns = sheet.ncols
                order_group = sheet.row_values(0).index('Group')
                date_planned = sheet.row_values(0).index('order_line/date_planned')
                product_id = sheet.row_values(0).index('order_line/product_id')
                line_name = sheet.row_values(0).index('order_line/name')
                price_unit = sheet.row_values(0).index('order_line/price_unit')
                product_qty = sheet.row_values(0).index('order_line/product_qty')
                taxes_id = sheet.row_values(0).index('order_line/taxes_id')
                partner_id = sheet.row_values(0).index('partner_id')
                pricelist_id = sheet.row_values(0).index('pricelist_id')
                picking_type_id = sheet.row_values(0).index('picking_type_id')
                invoice_method_name = sheet.row_values(0).index('invoice_method')
                notes = sheet.row_values(0).index('notes')
                for row_no in range(rows):
                    if row_no > 0:
                        order_group_value = sheet.row_values(row_no)[order_group]
                        error_line_vals = {'error_name' : '', 'error': False}
                        partner_value = sheet.row_values(row_no)[partner_id]
                        if partner_value:
                            if partner_value not in partner_dict.keys():
                                partner = self.env['res.partner'].search([('name', '=', partner_value)])
                                if not partner:
                                    error_line_vals['error_name'] = error_line_vals['error_name'] + 'Partner: ' + partner_value + ' Not Found! \n'
                                    error_line_vals['error'] = True
                                else:
                                    partner_dict[partner_value] = partner.id
                        
                        product_id_value = sheet.row_values(row_no)[product_id]
                        if product_id_value not in product_dict.keys():
                            product = self.env['product.product'].search([('default_code', '=', product_id_value)])
                            if not product:
                                error_line_vals['error_name'] = error_line_vals['error_name'] + 'Product: ' + product_id_value + ' Not Found! \n'
                                error_line_vals['error'] = True
                            else:
                                product_dict[product_id_value] = product.id
                        
                        pricelist_value = sheet.row_values(row_no)[pricelist_id]
                        if pricelist_value:
                            if pricelist_value not in pricelist_dict.keys():
                                pricelist = self.env['product.pricelist'].search([('name', '=', pricelist_value)])
                                if not pricelist:
                                    error_line_vals['error_name'] = error_line_vals['error_name'] + 'Pricelist: ' + pricelist_value + ' Not Found! \n'
                                    error_line_vals['error'] = True
                                else:
                                    pricelist_dict[pricelist_value] = pricelist.id
                        
                        invoice_method_value = sheet.row_values(row_no)[invoice_method_name]
                        
                        if not invoice_method_value in invoice_method_dict:
                            error_line_vals['error_name'] = error_line_vals['error_name'] + 'Invoice Method: ' + invoice_method_value + ' Not Found! \n'
                            error_line_vals['error'] = True
                            
                        invoice_method = invoice_method_dict[invoice_method_value]
                        
                        picking_type_value = sheet.row_values(row_no)[picking_type_id]
                        if picking_type_value:
                            if picking_type_value not in picking_dict:
                                picking_type = self.env['stock.picking.type'].search([('name', '=', picking_type_value)])
                                current_pick = False
                                for pick in picking_type:
                                    if pick.warehouse_id.company_id.id == self.env.user.company_id.id:
                                        current_pick = pick
                                picking_dict[picking_type_value] = current_pick
                        
                        taxes = []
                        tax_from_chunk = sheet.row_values(row_no)[taxes_id]
                        if tax_from_chunk:
                            tax_name_list = tax_from_chunk.split(',')
                            for tax_name in tax_name_list:
                                tax = self.env['account.tax'].search([('name', '=', tax_name)])
                                if not tax:
                                    error_line_vals['error_name'] = error_line_vals['error_name'] + 'Tax: ' + tax_name + ' Not Found! \n'
                                    error_line_vals['error'] = True
                                else:
                                    taxes.append(tax.id)
                        qty = float(sheet.row_values(row_no)[product_qty])
                        if qty < 0:
                            error_line_vals['error_name'] = error_line_vals['error_name'] + 'Quantity not less then zero! \n'
                            error_line_vals['error'] = True
                        
                        price_unit_value = float(sheet.row_values(row_no)[price_unit])
                        if price_unit_value < 0:
                            error_line_vals['error_name'] = error_line_vals['error_name'] + 'Price Unit not less then zero! \n'
                            error_line_vals['error'] = True
                        
                        if not error_log_id and error_line_vals['error']:
                            error_log_id = self.env['error.log'].create({'input_file': ir_attachment.id,
                                                                         'import_user_id' : self.env.user.id,
                                                                        'import_date': datetime.now(),
                                                                        'state': 'failed',
                                                                        'model_id': model.id}).id
                            error_line_id = self.env['error.log.line'].create({
                                                        'row_no' : row_no + 1,
                                                        'order_group' : order_group_value,
                                                        'error_name': error_line_vals['error_name'],
                                                        'log_id' : error_log_id
                                                    })
                        elif error_line_vals['error']:
                            error_line_id = self.env['error.log.line'].create({
                                                        'row_no' : row_no + 1,
                                                        'order_group' : order_group_value,
                                                        'error_name': error_line_vals['error_name'],
                                                        'log_id' : error_log_id
                                                    })
                        
                        order = sheet.row_values(row_no)[order_group]
                        if not error_log_id:
                            name = sheet.row_values(row_no)[line_name]
                            
                            product_data = self.env['purchase.order.line'].onchange_product_id(pricelist_dict[pricelist_value], product_dict[product_id_value], qty, False, partner_dict[partner_value],
                                                                                False, False, False, False, price_unit, 'draft')
                            if not name:
                                name = product_data['value']['name']
                            planned_date = sheet.row_values(row_no)[date_planned]
                            if not planned_date:
                                planned_date = product_data['value']['date_planned']
                            state = 'draft'
                            if order not in order_item_dict.keys():
                                order_item_dict[order] = [{
                                                    'name' : name,
                                                    'product_id' : product_dict[product_id_value],
                                                    'product_qty' : qty,
                                                    'date_planned' : planned_date,
                                                    'price_unit' : price_unit_value,
                                                    'state' : state,
                                                    'taxes_id': taxes,
                                                    }]
                            else:
                                order_item_dict[order].append({
                                                    'name' : name,
                                                    'product_id' : product_dict[product_id_value],
                                                    'product_qty' : qty,
                                                    'date_planned' : planned_date,
                                                    'price_unit' : price_unit_value,
                                                    'state' : state,
                                                    'taxes_id':taxes,
                                                    })
                            
                            if order_group_value not in order_dict:
                                pricelist_data = self.env['purchase.order'].onchange_pricelist(pricelist_dict[pricelist_value])
                                order_dict[order_group_value] = {
                                                'partner_id' : partner_dict[partner_value],
                                                'pricelist_id' : pricelist_dict[pricelist_value],
                                                'location_id': picking_dict[picking_type_value].default_location_dest_id and picking_dict[picking_type_value].default_location_dest_id.id,
                                                'invoice_method': invoice_method,
                                                'currency_id' : pricelist_data['value']['currency_id'],
                                                'date_order' : planned_date,
                                                'notes': sheet.row_values(row_no)[notes]
                                                }
                                
                if not error_log_id:
                    error_log_id = self.env['error.log'].create({'input_file': ir_attachment.id,
                                                                 'import_user_id' : self.env.user.id,
                                                                 'import_date': datetime.now(),
                                                                 'state': 'done',
                                                                 'model_id': model.id}).id
                                                                    
                    for item in order_item_dict:
                        order_data = order_dict[item]
                        order_vals = {
                            'partner_id' : order_data['partner_id'],
                            'pricelist_id' : order_data['pricelist_id'],
                            'location_id': order_data['location_id'],
                            'invoice_method': order_data['invoice_method'],
                            'imported_order' : True,
                            'order_ref': item,
                            'currency_id': order_data['currency_id'],
                            'date_order' : order_data['date_order'],
                            'notes': order_data['notes'],
                        }
                        order_id = self.env['purchase.order'].create(order_vals)
                        for po_line in order_item_dict[item]:
                            orderline_vals = {
                                'name' : po_line['name'],
                                'product_id' : po_line['product_id'],
                                'product_qty' : po_line['product_qty'],
                                'date_planned' : po_line['date_planned'],
                                'price_unit' : po_line['price_unit'],
                                'state' : po_line['state'],
                                'taxes_id': [(6, 0, po_line['taxes_id'])],
                                'order_id' : order_id.id,
                            }
                            orderline_id = self.env['purchase.order.line'].create(orderline_vals)
                        order_id.signal_workflow('purchase_confirm')
                        if order_id.invoice_ids:
                            for invoice in order_id.invoice_ids:
                                invoice.journal_id = self.supplier_invoice_journal_id.id
                                if invoice.state == 'draft':
                                    invoice.signal_workflow('invoice_open')
                                    journal_data = self.env['account.voucher'].onchange_journal_voucher(line_ids= False, tax_id=False, price=0.0, partner_id=invoice.partner_id.id, journal_id=invoice.journal_id.id, ttype=False, company_id=invoice.company_id.id)
                                    partner_data  = self.env['account.voucher'].onchange_partner_id(invoice.partner_id.id, 
                                                                                                invoice.journal_id.id, invoice.amount_total , invoice.currency_id.id, 'payment', invoice.date_invoice)
                                    line_dr_list = []
                                    for line in partner_data['value']['line_dr_ids']:
                                        moveline = self.env['account.move.line'].browse(line['move_line_id'])
                                        if invoice.id == moveline.invoice.id:
                                            line_dr_list.append((0, 0, line))
                                    voucher_vals = {
                                        'name': '/',
                                        'partner_id' : invoice.partner_id.id,
                                        'company_id' : invoice.company_id.id,
                                        'journal_id' : self.supplier_payment_journal_id.id,
                                        'currency_id': partner_data['value']['currency_id'],
                                        'line_ids' : False,
                                        'line_cr_ids' : False,
                                        'line_dr_ids' : line_dr_list,
                                        'account_id' : partner_data['value']['account_id'],
                                        'period_id': journal_data['value']['period_id'],
                                        'state': 'draft',
                                        'date' : invoice.date_invoice,
                                        'type': 'payment',
                                        'amount' : invoice.amount_total,
                                    }
                                    voucher_id = self.env['account.voucher'].create(voucher_vals)
                                    voucher_id.signal_workflow('proforma_voucher')
                         
            result = self.env.ref('base_import_log.error_log_action')
            result = result.read()[0]
            result['domain'] = str([('id','in',[error_log_id])])
            return result

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
