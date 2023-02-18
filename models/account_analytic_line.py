from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    work_type_id = fields.Many2one(string="Work Type",
                                   comodel_name="hr.timesheet.work_type",
                                   help="Odaberi vrstu rada",
                                   required=True)
    # worked_days_id = fields.Many2one(string="Payslip",
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

    # @api.constrains('unit_amount')
    # def _check_unit_amount(self):
    #  #if not isinstance(self.ancestor_task_id, models.BaseModel):
    #  #   return
    #  for rec in self:
    #     if rec.unit_amount < 1:
    #           raise ValidationError(_('Broj sati mora biti > 0'))

    # def write(self, vals):
    #    #if 'unit_amount' in vals:
    #    if self.unit_amount < 1:
    #       raise UserError(_('Belaj sihtarica sati < 0.'))
    #    return super(AccountAnalyticLine, self).write(vals)


    # analytic_line unit_amount = 8, hours_to_spend = 3
    # => we need two analytic lines: 3 + 5
    def split_as_needed(self, hours_to_spend):
        amount_to_split = self.unit_amount
        name_to_split = self.name.strip()
        if hours_to_spend > 0 and hours_to_spend < amount_to_split:
            self.write({'unit_amount': hours_to_spend,
                        'name': name_to_split + ' split-1'})
            self.copy({'unit_amount': amount_to_split - hours_to_spend,
                       'name': name_to_split + 'split-2'})


class ProjectTask(models.Model):
    _inherit = "project.task"
    @api.constrains('timesheet_ids')
    def _check_timesheet_unit_amount(self):
        for timesheet in self.timesheet_ids:
            if timesheet.unit_amount < 1:
                raise ValidationError(_('Broj sati mora biti > 0'))
            if timesheet.unit_amount > 16:
                raise ValidationError(_('Broj sati mora biti <= 16'))
