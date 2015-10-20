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
    
    input_file = fields.Binary('Purchase Order File (.xlsx Format)', required=True)
    datas_fname = fields.Char('File Path')
    supplier_invoice_journal_id = fields.Many2one('account.journal', string='Supplier Invoice Journal', default=_get_supplier_invoice_journal_id)
    supplier_payment_journal_id = fields.Many2one('account.journal', string='Supplier Payment Journal', default=_get_supplier_payment_journal_id)

    
    @api.model
    def _get_partner_dict(self, partner_value, partner_dict, error_line_vals):
        if partner_value not in partner_dict.keys():
            partner = self.env['res.partner'].search([('name', '=', partner_value)])
            if not partner:
                error_line_vals['error_name'] = error_line_vals['error_name'] + 'Partner: ' + partner_value + ' Not Found! \n'
                error_line_vals['error'] = True
            else:
                partner_dict[partner_value] = partner.id

    @api.model
    def _get_product_dict(self, product_id_value, product_dict, error_line_vals):
        if product_id_value not in product_dict.keys():
            product = self.env['product.product'].search([('default_code', '=', product_id_value)])
            if not product:
                error_line_vals['error_name'] = error_line_vals['error_name'] + 'Product: ' + product_id_value + ' Not Found! \n'
                error_line_vals['error'] = True
            else:
                product_dict[product_id_value] = product.id

    @api.model
    def _get_pricelist_dict(self, pricelist_value, pricelist_dict, error_line_vals):
        if pricelist_value not in pricelist_dict.keys():
            pricelist = self.env['product.pricelist'].search([('name', '=', pricelist_value)])
            if not pricelist:
                error_line_vals['error_name'] = error_line_vals['error_name'] + 'Pricelist: ' + pricelist_value + ' Not Found! \n'
                error_line_vals['error'] = True
            else:
                pricelist_dict[pricelist_value] = pricelist.id

    @api.model
    def _get_invoice_method(self, invoice_method_value, error_line_vals):
        invoice_method_dict = {'Based on Purchase Order lines' : 'manual',
                              'Based on generated draft invoice' : 'order',
                              'Based on incoming shipments' : 'picking'}
        if not invoice_method_value in invoice_method_dict:
            error_line_vals['error_name'] = error_line_vals['error_name'] + 'Invoice Method: ' + invoice_method_value + ' Not Found! \n'
            error_line_vals['error'] = True
        return invoice_method_dict[invoice_method_value]
    
    @api.model
    def _get_picking_dict(self, warehouse_value, picking_dict, error_line_vals):
        warehouse_id = self.env['stock.warehouse'].search([('name','=',warehouse_value)]).id
        if not warehouse_id:
            error_line_vals['error_name'] = error_line_vals['error_name'] + 'Warehouse: ' + warehouse_value + ' Not Found! \n'
            error_line_vals['error'] = True
        else:
            picking_type = self.env['stock.picking.type'].search([('warehouse_id','=',warehouse_id),('code','=','incoming')])
            picking_dict[warehouse_value] = picking_type

    @api.model
    def _get_taxes(self, tax_from_chunk, taxes, error_line_vals):
        tax_name_list = tax_from_chunk.split(',')
        for tax_name in tax_name_list:
            tax = self.env['account.tax'].search([('name', '=', tax_name)])
            if not tax:
                error_line_vals['error_name'] = error_line_vals['error_name'] + 'Tax: ' + tax_name + ' Not Found! \n'
                error_line_vals['error'] = True
            else:
                taxes.append(tax.id)

    @api.model
    def _update_error_log(self, error_log_id, error_line_vals, ir_attachment, model, row_no, order_group_value):
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
        return error_log_id

    @api.model
    def _get_order_id(self, order_data, item, error_log_id):
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
            'error_log_id': error_log_id,
        }
        return self.env['purchase.order'].create(order_vals)

    @api.model
    def _get_orderline_id(self, po_line, order_id):
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
        return self.env['purchase.order.line'].create(orderline_vals)


    @api.multi
    def import_purchase_data(self):
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
                warehouse_id = sheet.row_values(0).index('Warehouse')
                invoice_method_name = sheet.row_values(0).index('invoice_method')
                notes = sheet.row_values(0).index('notes')

                for row_no in range(1, rows):  # skip the first row
                    order_group_value = sheet.row_values(row_no)[order_group]
                    error_line_vals = {'error_name' : '', 'error': False}
                    partner_value = sheet.row_values(row_no)[partner_id]
                    if partner_value:
                        self._get_partner_dict(partner_value, partner_dict, error_line_vals)
                    
                    product_id_value = sheet.row_values(row_no)[product_id]
                    if product_id_value:
                        self._get_product_dict(product_id_value, product_dict, error_line_vals)
                    
                    pricelist_value = sheet.row_values(row_no)[pricelist_id]
                    if pricelist_value:
                        self._get_pricelist_dict(pricelist_value, pricelist_dict, error_line_vals)
                    
                    invoice_method_value = sheet.row_values(row_no)[invoice_method_name]
                    invoice_method = self._get_invoice_method(invoice_method_value, error_line_vals)
                    
                    warehouse_value = sheet.row_values(row_no)[warehouse_id]
                    if warehouse_value:
                        self._get_picking_dict(warehouse_value, picking_dict, error_line_vals)
                    
                    taxes = []
                    tax_from_chunk = sheet.row_values(row_no)[taxes_id]
                    if tax_from_chunk:
                        self._get_taxes(tax_from_chunk, taxes, error_line_vals)

                    qty = float(sheet.row_values(row_no)[product_qty])
                    if qty < 0:
                        error_line_vals['error_name'] = error_line_vals['error_name'] + 'Quantity not less then zero! \n'
                        error_line_vals['error'] = True
                    
                    price_unit_value = float(sheet.row_values(row_no)[price_unit])
                    if price_unit_value < 0:
                        error_line_vals['error_name'] = error_line_vals['error_name'] + 'Price Unit not less then zero! \n'
                        error_line_vals['error'] = True
                    
                    error_log_id = self._update_error_log(error_log_id, error_line_vals, ir_attachment, model, row_no, order_group_value)
                    
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
                                            'location_id': picking_dict[warehouse_value].default_location_dest_id and picking_dict[warehouse_value].default_location_dest_id.id,
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
                        order_id = self._get_order_id(order_dict[item], item, error_log_id)
                        
                        for po_line in order_item_dict[item]:
                            orderline_id = self._get_orderline_id(po_line, order_id)

                        order_id.signal_workflow('purchase_confirm')
                        
                        if order_id.invoice_ids:
                            for invoice in order_id.invoice_ids:
                                invoice.journal_id = self.supplier_invoice_journal_id.id
                                if invoice.state == 'draft':
                                    invoice.signal_workflow('invoice_open')
                                    if self.supplier_payment_journal_id.currency and self.supplier_payment_journal_id.currency.id != invoice.currency_id.id:
                                        currency_id_voucher = self.supplier_payment_journal_id.currency.id
                                        voucher_amount = invoice.currency_id.compute(invoice.amount_total, self.supplier_payment_journal_id.currency)
                                    elif not self.supplier_payment_journal_id.currency and invoice.currency_id.id != invoice.company_id.currency_id.id:
                                        currency_id_voucher = invoice.company_id.currency_id.id
                                        voucher_amount = invoice.currency_id.compute(invoice.amount_total, invoice.company_id.currency_id)
                                    else:
                                        currency_id_voucher = invoice.currency_id.id
                                        voucher_amount = invoice.amount_total
                                    partner_data  = self.env['account.voucher'].onchange_partner_id(invoice.partner_id.id,
                                                                                                    self.supplier_payment_journal_id.id,
                                                                                                    voucher_amount,
                                                                                                    currency_id_voucher,
                                                                                                    'payment',
                                                                                                    invoice.date_invoice)
                                    journal_data = self.env['account.voucher'].onchange_journal_voucher(line_ids= False,
                                                                                                        tax_id=False,
                                                                                                        price=0.0, 
                                                                                                        partner_id=invoice.partner_id.id,
                                                                                            journal_id=self.supplier_payment_journal_id.id,
                                                                                                        ttype='payment',
                                                                                                        company_id=invoice.company_id.id)
                                    line_dr_list = []
                                    for line in partner_data['value']['line_dr_ids']:
                                        moveline = self.env['account.move.line'].browse(line['move_line_id'])
                                        if invoice.id == moveline.invoice.id:
                                            line['amount'] = voucher_amount
                                            line_dr_list.append((0, 0, line))
                                            break #IF one line found then get out of loop since invoice and payment has one to one relation.
                                    voucher_vals = {
                                        'name': '/',
                                        'partner_id' : invoice.partner_id.id,
                                        'company_id' : invoice.company_id.id,
                                        'journal_id' : self.supplier_payment_journal_id.id,
                                        'currency_id': currency_id_voucher,
                                        'line_ids' : False,
                                        'line_cr_ids' : False,
                                        'line_dr_ids' : line_dr_list,
                                        'account_id' : partner_data['value']['account_id'],
                                        'period_id': journal_data['value']['period_id'],
                                        'state': 'draft',
                                        'date' : invoice.date_invoice,
                                        'type': 'payment',
                                        'amount' : voucher_amount,
                                        'payment_rate': journal_data['value']['payment_rate'],
                                        'payment_rate_currency_id': journal_data['value']['payment_rate_currency_id']
                                    }
                                    voucher_id = self.env['account.voucher'].create(voucher_vals)
                                    voucher_id.signal_workflow('proforma_voucher')
                         
            res = self.env.ref('base_import_log.error_log_action')
            res = res.read()[0]
            res['domain'] = str([('id','in',[error_log_id])])
            return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
