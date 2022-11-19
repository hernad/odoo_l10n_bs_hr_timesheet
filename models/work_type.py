from odoo import models, fields
#from odoo.tools.translate import _

class TimesheetsWorkType(models.Model):
    _name = 'hr.timesheet.work_type'
    _description = 'Timesheet Work Types'
    _order = "code"

    name = fields.Char("Work Type", required=True, translate=True)
    code = fields.Char("Code", required=True)
    food_included = fields.Boolean("Food included?", required=True, default=True)
    hours_fond_included = fields.Boolean("Included in hours fond", required=True, default=True)


