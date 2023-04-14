from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class HrPayslipTimesheet(models.Model):
    _inherit = "hr.payslip"

    timesheet_hours = fields.Float(
        string="Šihtarice",
        compute="_compute_field_timesheet_hours",
        store=False
    )

    timesheet_ids = fields.One2many(
        "account.analytic.line",
        compute="_compute_timesheet_ids",
        string="Šihtarice",
        store=False
    )

    timesheet_unspent_ids = fields.One2many(
        "account.analytic.line",
        compute="_compute_timesheet_unspent_ids",
        string="Šihtarice za preraspodjelu",
        store=False
    )

    timesheet_spent_current_ids = fields.One2many(
        "account.analytic.line",
        compute="_compute_timesheet_spent_current_ids",
        string="Šihtarice tekućeg mjeseca (potrošene)",
        store=False
    )

    timesheet_spent_old_ids = fields.One2many(
        "account.analytic.line",
        compute="_compute_timesheet_spent_old_ids",
        string="Šihtarice potrošene u ovom mjesecu iz preraspodjele",
        store=False
    )

    @api.depends("worked_days_line_ids")
    def _compute_field_timesheet_hours(self):
        analytic_line_object = self.env['account.analytic.line']
        for payslip in self:
            lines = analytic_line_object.search([
                ('employee_id', '=', payslip.employee_id.id),
                ('date', '<=', payslip.date_to),
                ('date', '>=', payslip.date_from),
                ('work_type_id', '!=', False),
                ('global_leave_id', '=', False),
                ('holiday_id', '=', False),
            ], order="date desc")
            hours_total = 0
            for line in lines:
                hours_total += line.unit_amount
            payslip.timesheet_hours = hours_total

    @api.depends("worked_days_line_ids")
    def _compute_timesheet_ids(self):
        analytic_line_object = self.env['account.analytic.line']
        for payslip in self:
            lines = analytic_line_object.search([
                        ('employee_id', '=', payslip.employee_id.id),
                        ('date', '<=', payslip.date_to),
                        ('work_type_id', '!=', False),
                        ('global_leave_id', '=', False),
                        ('holiday_id', '=', False),
                        #('worked_days_ids', '=', False)
                        # timesheet not spent (False) or this worked_days_ids exist in current worked_days_line_ids
                        #'|', ('worked_days_ids', '=', False),
                        #     ('worked_days_ids', 'in', [line.id for line in self.worked_days_line_ids])
                    ], order="date desc")
            payslip.timesheet_ids = lines


    @api.depends("worked_days_line_ids")
    def _compute_timesheet_unspent_ids(self):
        def sihtarica_potrosena_u_buducnost(payslip_date, timesheet_spent):            
            if payslip_date < timesheet_spent:
               # payslip_date = 28.02.2023
               # timesheet_spent = 01.05.2023 
               # šitarica potrošena u budućnosti
               return True

        analytic_line_object = self.env['account.analytic.line']
        for payslip in self:
            lines = analytic_line_object.search([
                        ('employee_id', '=', payslip.employee_id.id),
                        ('date', '<=', payslip.date_to),
                        ('work_type_id', '!=', False),
                        ('global_leave_id', '=', False),
                        ('holiday_id', '=', False)
                    ], order="date desc")
            # line.in_payroll = False znaci da nema pridruzene plate      
            payslip.timesheet_unspent_ids = lines.filtered(lambda line: 
                     not line.in_payroll or sihtarica_potrosena_u_buducnost(payslip.date_to, line.in_payroll)
                    )

    @api.depends("worked_days_line_ids")
    def _compute_timesheet_spent_current_ids(self):

        analytic_line_object = self.env['account.analytic.line']
        for payslip in self:
            lines = analytic_line_object.search([
                        ('employee_id', '=', payslip.employee_id.id),
                        ('date', '<=', payslip.date_to),
                        ('work_type_id', '!=', False),
                        ('global_leave_id', '=', False),
                        ('holiday_id', '=', False)
                    ], order="date desc")
            # sihtarice iz tekuceg mjeseca potrosene u tom mjesecu     
            payslip.timesheet_spent_current_ids = lines.filtered(lambda line: 
                (line.date.year == payslip.date_to.year and line.date.month == payslip.date_to.month) and
                (line.in_payroll and line.in_payroll == payslip.date_to)
            )


    @api.depends("worked_days_line_ids")
    def _compute_timesheet_spent_old_ids(self):

        analytic_line_object = self.env['account.analytic.line']
        for payslip in self:
            lines = analytic_line_object.search([
                        ('employee_id', '=', payslip.employee_id.id),
                        ('date', '<=', payslip.date_to),
                        ('work_type_id', '!=', False),
                        ('global_leave_id', '=', False),
                        ('holiday_id', '=', False),
                    ], order="date desc")
            # sihtarice iz predhodnih mjeseci potrosene u ovom mjesecu     
            payslip.timesheet_spent_old_ids = lines.filtered(lambda line: 
                     (payslip.date_from > line.date) and
                     (line.in_payroll and line.in_payroll == payslip.date_to)
                    )                                