from odoo import models, fields

class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    work_type_id = fields.Many2one(string="Work Type",
                                   comodel_name="hr.timesheet.work_type",
                                   help="Odaberi vrstu rada")
    #worked_days_id = fields.Many2one(string="Payslip",
    #                                 comodel_name="hr.payslip.worked_days")

    worked_days_ids = fields.Many2many(
       string="Worked days",
       comodel_name="hr.payslip.worked_days",
       relation="hr_payslip_analytic_rel",
       # model records
       column1="analytic_line_id",
       # related model records
       column2="worked_days_id",
       inverse_name="id"
    )
