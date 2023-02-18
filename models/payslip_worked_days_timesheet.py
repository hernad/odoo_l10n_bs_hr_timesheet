from odoo import models, fields



# select employee_id,* from hr_payslip_worked_days
#      left join hr_payslip_analytic_rel on hr_payslip_worked_days.id=hr_payslip_analytic_rel.worked_days_id
#      left join account_analytic_line on account_analytic_line.id=hr_payslip_analytic_rel.analytic_line_id
#      where employee_id=24

class HrPayslipAnalytic(models.Model):
    _inherit = "hr.payslip.worked_days"

    timesheet_item_ids = fields.Many2many(
       string="Timesheet items",
       comodel_name="account.analytic.line",
       relation="hr_payslip_analytic_rel",
       # model records
       column1="worked_days_id",
       # related model records
       column2="analytic_line_id",
       inverse_name="worked_days_ids"
    )
