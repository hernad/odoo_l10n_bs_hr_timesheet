from odoo import api, models, fields
#from odoo.tools.translate import _

class TimesheetsWorkType(models.Model):
    _name = 'hr.timesheet.work_type'
    _description = 'Timesheet Work Types'
    _order = "code"

    name = fields.Char("Work Type", required=True, translate=True)
    code = fields.Char("Code", required=True)


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    work_type_id = fields.Many2one(string="Work Type", comodel_name="hr.timesheet.work_type", help="Odaberi vrstu rada" )

