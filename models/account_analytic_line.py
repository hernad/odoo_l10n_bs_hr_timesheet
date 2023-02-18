from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    in_payroll = fields.Char(string="Plata", compute="_calc_in_payroll")
    work_type_id = fields.Many2one(string="Work Type",
                                   comodel_name="hr.timesheet.work_type",
                                   help="Odaberi vrstu rada",
                                   required=True)

    work_type_code = fields.Char('Work type code', compute='_compute_work_type_code')

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
        inverse_name="timesheet_item_ids"
    )

    @api.depends('work_type_id')
    def _compute_work_type_code(self):
        for rec in self:
            rec.work_type_code = rec.work_type_id.code

    @api.depends('worked_days_ids')
    # timesheet item spent in payroll
    def _calc_in_payroll(self):
        for rec in self:
            if rec.worked_days_ids:
                rec.in_payroll = 'X'
            else:
                rec.in_payroll = ' '

    def unlink(self):
        for rec in self:
            if rec.in_payroll == 'X':
                raise(ValidationError("Šihtarica iskorištena u obračunu se ne može brisati!"))
        return super(AccountAnalyticLine, self).unlink()


    def write(self, vals):
        if any(in_payroll == 'X' for in_payroll in set(self.mapped('in_payroll'))):
            raise UserError(_("Šihtarica iskorištena u obračunu - ne čačkaj mečku!"))
        else:
            return super(AccountAnalyticLine, self).write(vals)

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
    def split_as_needed(self, hours_to_spend, food_days_rest):
        amount_to_split = self.unit_amount
        name_to_split = self.name.strip()
        work_type_id_1 = self.work_type_id
        work_type_id_2 = work_type_id_1

        if hours_to_spend > 0 and hours_to_spend < amount_to_split:
            work_type_old = work_type_id_1
            if work_type_old.food_included:
                env_db_work_type = self.env['hr.timesheet.work_type']
                if work_type_old.code == "10_SF":
                    work_type_new = env_db_work_type.search([("code", '=', '11_S')])
                elif work_type_old.code == "20_NF":
                    work_type_new = env_db_work_type.search([("code", '=', '21_N')])
                elif work_type_old.code == "30_WF":
                    work_type_new = env_db_work_type.search([("code", '=', '31_W')])
                else:
                    raise(ValidationError('Način rada: ' + work_type_old.code + ' mora imati varijantu bez TO'))

                if food_days_rest <= 0:
                    # we have reached food days limit
                    work_type_id_1 = work_type_new
                    work_type_id_2 = work_type_old
                else:
                    work_type_id_1 = work_type_old
                    work_type_id_2 = work_type_new

            self.write({
                    'unit_amount': hours_to_spend,
                    'name': 'split1: ' + name_to_split,
                    'work_type_id': work_type_id_1.id
            })
            self.copy({
                'unit_amount': amount_to_split - hours_to_spend,
                'name': 'split2: ' + name_to_split,
                'work_type_id': work_type_id_2.id
            })

        return

class ProjectTask(models.Model):
    _inherit = "project.task"
    @api.constrains('timesheet_ids')
    def _check_timesheet_unit_amount(self):
        for timesheet in self.timesheet_ids:
            if timesheet.unit_amount < 1:
                raise ValidationError(_('Broj sati mora biti > 0'))
            if timesheet.unit_amount > 16:
                raise ValidationError(_('Broj sati mora biti <= 16'))
