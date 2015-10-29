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

import os
import csv
import StringIO
from tempfile import TemporaryFile
from openerp import models, fields, api, _
from datetime import datetime
import base64
# import xlrd
from openerp import tools
import sys
import urllib
from openerp.exceptions import except_orm, Warning, RedirectWarning


class import_picking(models.TransientModel):
    _name = 'import.picking'
    
    input_file = fields.Binary('Import Picking File (.CSV Format)', required=True)
    datas_fname = fields.Char('File Path')
    picking_type = fields.Selection([('purchase', 'Purchase'), ('sale', 'Sale')], string='Picking Type', required=True)


    @api.model
    def _update_error_log(self, error_log_id, error_line_vals, ir_attachment, model, row_no, order_group_value):
        if not error_log_id and error_line_vals['error']:
            error_log_id = self.env['error.log'].create({'input_file': ir_attachment.id,
                                                         'import_user_id' : self.env.user.id,
                                                        'import_date': datetime.now(),
                                                        'state': 'failed',
                                                        'model_id': model.id,
                                                        'picking_type': error_line_vals['picking_type']}).id
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
    def _check_csv_format(self, row):
        for r in row:
            try:
                r.decode('utf-8')
            except:
                raise Warning(_('Import Error!'),_('Please prepare a CSV file with UTF-8 encoding.!'))
    
    @api.model
    def _process_purchase_invoice(self, picking, order_id):
        default_journals = self.env['purchase.import.default'].search([])
        supplier_payment_journal = default_journals.supplier_payment_journal_id
        supplier_invoice_journal = default_journals.supplier_invoice_journal_id
        invoice_ids = picking.action_invoice_create(
                journal_id = supplier_invoice_journal.id,
                type = 'in_invoice'
                )
        if order_id.invoice_ids:
            for invoice in order_id.invoice_ids:
                invoice.journal_id = supplier_invoice_journal.id
                if invoice.state == 'draft':
                    invoice.signal_workflow('invoice_open')
                    if supplier_payment_journal.currency and supplier_payment_journal.currency.id != invoice.currency_id.id:
                        currency_id_voucher = supplier_payment_journal.currency.id
                        voucher_amount = invoice.currency_id.compute(invoice.amount_total, self.supplier_payment_journal_id.currency)
                    elif not supplier_payment_journal.currency and invoice.currency_id.id != invoice.company_id.currency_id.id:
                        currency_id_voucher = invoice.company_id.currency_id.id
                        voucher_amount = invoice.currency_id.compute(invoice.amount_total, invoice.company_id.currency_id)
                    else:
                        currency_id_voucher = invoice.currency_id.id
                        voucher_amount = invoice.amount_total
                    partner_data  = self.env['account.voucher'].onchange_partner_id(invoice.partner_id.id,
                                                                                    supplier_payment_journal.id,
                                                                                    voucher_amount,
                                                                                    currency_id_voucher,
                                                                                    'payment',
                                                                                    invoice.date_invoice)
                    journal_data = self.env['account.voucher'].onchange_journal_voucher(line_ids= False,
                                                                                        tax_id=False,
                                                                                        price=0.0, 
                                                                                        partner_id=invoice.partner_id.id,
                                                                                        journal_id=supplier_payment_journal.id,
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
                        'journal_id' : supplier_payment_journal.id,
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
    
    @api.model
    def _process_sale_invoice(self, picking, order_id):
        default_journals = self.env['sale.import.default'].search([])
        customer_payment_journal = default_journals.customer_payment_journal_id
        customer_invoice_journal = default_journals.customer_invoice_journal_id
        invoice_ids = picking.action_invoice_create(
                journal_id = customer_invoice_journal.id,
                type = 'out_invoice'
                )
        if order_id.invoice_ids:
            for invoice in order_id.invoice_ids:
                invoice.journal_id = customer_invoice_journal.id
                if invoice.state == 'draft':
                    invoice.signal_workflow('invoice_open')
                    if customer_payment_journal.currency and customer_payment_journal.currency.id != invoice.currency_id.id:
                        currency_id_voucher = customer_payment_journal.currency.id
                        voucher_amount = invoice.currency_id.compute(invoice.amount_total, customer_payment_journal.currency)
                    elif not customer_payment_journal.currency and invoice.currency_id.id != invoice.company_id.currency_id.id:
                        currency_id_voucher = invoice.company_id.currency_id.id
                        voucher_amount = invoice.currency_id.compute(invoice.amount_total, invoice.company_id.currency_id)
                    else:
                        currency_id_voucher = invoice.currency_id.id
                        voucher_amount = invoice.amount_total
                    partner_data  = self.env['account.voucher'].onchange_partner_id(invoice.partner_id.id,
                                                                                    customer_payment_journal.id,
                                                                                    voucher_amount,
                                                                                    currency_id_voucher,
                                                                                    'receipt',
                                                                                    invoice.date_invoice)
                    journal_data = self.env['account.voucher'].onchange_journal_voucher(line_ids= False,
                                                                                        tax_id=False,
                                                                                        price=0.0, 
                                                                                        partner_id=invoice.partner_id.id,
                                                                                        journal_id=customer_payment_journal.id,
                                                                                        ttype='receipt',
                                                                                        company_id=invoice.company_id.id)
                    line_cr_list = []
                    for line in partner_data['value']['line_cr_ids']:
                        moveline = self.env['account.move.line'].browse(line['move_line_id'])
                        if invoice.id == moveline.invoice.id:
                            line['amount'] = voucher_amount
                            line_cr_list.append((0, 0, line))
                            break #IF one line found then get out of loop since invoice and payment has one to one relation.
                    voucher_vals = {
                        'name': '/',
                        'partner_id' : invoice.partner_id.id,
                        'company_id' : invoice.company_id.id,
                        'journal_id' : customer_payment_journal.id,
                        'currency_id': currency_id_voucher,
                        'line_ids' : False,
                        'line_cr_ids' : line_cr_list,
                        'line_dr_ids' : False,
                        'account_id' : partner_data['value']['account_id'],
                        'period_id': journal_data['value']['period_id'],
                        'state': 'draft',
                        'date' : invoice.date_invoice,
                        'type': 'receipt',
                        'amount' : voucher_amount,
                        'payment_rate': journal_data['value']['payment_rate'],
                        'payment_rate_currency_id': journal_data['value']['payment_rate_currency_id']
                    }
                    voucher_id = self.env['account.voucher'].create(voucher_vals)
                    voucher_id.signal_workflow('proforma_voucher')
    
    @api.model
    def _purchase_picking_process(self, order_number, error_line_vals):
        order_id = self.env['purchase.order'].search([('name', 'ilike', order_number)])
        picking_ids = []
        if not order_id:
            error_line_vals['error_name'] = error_line_vals['error_name'] + 'Order: ' + order_number + ' Not Found! \n'
            error_line_vals['error'] = True
            error_line_vals.update({'picking_type':'purchase'})
        else:
            if order_id.picking_ids:
                for picking in order_id.picking_ids:
                    if not picking.state == 'done' and not picking.state == 'cancel':
                        picking.action_assign()
                        if picking.state == 'assigned':
                            picking_ids.append(picking)
                            picking.do_transfer()
                            if picking.invoice_state == '2binvoiced':
                                self._process_purchase_invoice(picking, order_id)
                        else:
                            error_line_vals['error_name'] = error_line_vals['error_name'] + 'Picking State: ' + picking.state + ' Not Ready to Transfer! \n'
                            error_line_vals['error'] = True
                            error_line_vals.update({'picking_type':'purchase'})
        return picking_ids

    @api.model
    def _sale_picking_process(self, order_number, error_line_vals):
        order_id = self.env['sale.order'].search([('name', 'ilike', order_number)])
        picking_ids = []
        if not order_id:
            error_line_vals['error_name'] = error_line_vals['error_name'] + 'Order: ' + order_number + ' Not Found! \n'
            error_line_vals['error'] = True
            error_line_vals.update({'picking_type':'sale'})
        else:
            if order_id.picking_ids:
                for picking in order_id.picking_ids:
                    if not picking.state == 'done' and not picking.state == 'cancel':
                        picking.action_assign()
                        if picking.state == 'assigned':
                            picking_ids.append(picking)
                            picking.do_transfer()
                            if picking.invoice_state == '2binvoiced':
                                self._process_sale_invoice(picking, order_id)
                        else:
                            error_line_vals['error_name'] = error_line_vals['error_name'] + 'Picking State is ' + 'Waiting Availibility ' + ' so picking could not be transferred. Please make sure stock is available in warehouse to process this picking.\n'
                            error_line_vals['error'] = True
                            error_line_vals.update({'picking_type':'sale' })
        return picking_ids
                    

    @api.multi
    def import_picking_data(self):
        
        for line in self:
            model = self.env['ir.model'].search([('model', '=', 'stock.picking')])
            error_log_id = False
             
            ir_attachment = self.env['ir.attachment'].create({'name': self.datas_fname,
                        'datas': self.input_file,
                        'datas_fname': self.datas_fname})
              
            fileobj = TemporaryFile('w+')
            fileobj.write(base64.decodestring(self.input_file))
            fileobj.seek(0)
            reader = csv.reader(fileobj)
            
            sale_picking_ids = []
            purchase_picking_ids = []
            line = 0
            log_ids = []
            for row in reader:
                line += 1
                if line == 1:#Get the index of header and skip the first line
                    number = row.index('Number')
                    continue
                order_number = row[number].strip()
                error_line_vals = {'error_name' : '', 'error': False}

                if line == 2:#Check for UTF-8 Format. Only for first line i.e. line=2.
                    self._check_csv_format(row)

                if order_number:
                    if self.picking_type == 'sale':
                        successed_picking_ids = self._sale_picking_process(order_number, error_line_vals)
                        sale_picking_ids.extend(successed_picking_ids)
                    else:
                        successed_picking_ids = self._purchase_picking_process(order_number, error_line_vals)
                        purchase_picking_ids.extend(successed_picking_ids)

                error_log_id = self._update_error_log(error_log_id, error_line_vals, ir_attachment, model, line, order_number)
            if not error_log_id:
                error_log_id = self.env['error.log'].create({'input_file': ir_attachment.id,
                                                             'import_user_id' : self.env.user.id,
                                                             'import_date': datetime.now(),
                                                             'state': 'done',
                                                             'model_id': model.id,
                                                             'picking_type': self.picking_type}).id
                for pick in sale_picking_ids:
                    pick.sale_error_log_id = error_log_id
                    
                for pick in purchase_picking_ids:
                    pick.purchase_error_log_id = error_log_id
                                                                 
                      
            res = self.env.ref('base_import_log.error_log_action')
            res = res.read()[0]
            res['domain'] = str([('id','in',[error_log_id])])
            return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
