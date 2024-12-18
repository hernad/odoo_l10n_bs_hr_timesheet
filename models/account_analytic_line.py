from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import timedelta

class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    default_project_id = fields.Integer(compute='_default_project_id', store=False)
    default_task_id = fields.Integer(compute='_default_task_id', store=False)
    default_date = fields.Date(compute='_default_date', store=False)
    default_work_type_id = fields.Integer(compute='_default_work_type_id', store=False)
    default_unit_amount = fields.Float(compute='_default_unit_amount', store=False)
    default_employee_id = fields.Integer(compute='_default_employee_id', store=False)


    in_payroll = fields.Date(
       string="Plata", 
       compute="_calc_in_payroll",
       search="_search_in_payroll"
    )
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
 
    def set_default_data_entry_values(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'user.timesheet.options.wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'views': [[False, 'form']],
            'target': 'new',
        }

    @api.model
    def default_get(self, fields_list):
    
        values = super().default_get(fields_list)
        user_options = self.env["res.users.options"].search([
            ('user_id', '=', self.env.user.id)
        ])
    
        if user_options:
            values.update({        
                "project_id": user_options.data_entry_project_id,
                "task_id": user_options.data_entry_task_id,
                "date": user_options.data_entry_date,
                "employee_id": user_options.data_entry_employee_id,
                "work_type_id": user_options.data_entry_work_type_id,
                "unit_amount": user_options.data_entry_unit_amount
                #"name": self.env.user.name
            })

        return values

    @api.model
    def create(self, vals):
        acc_line = super(AccountAnalyticLine, self).create(vals)
        return acc_line

    def write(self, vals):
        if any(in_payroll for in_payroll in set(self.mapped('in_payroll'))):
            raise UserError(_("Šihtarica iskorištena u obračunu - ne čačkaj mečku!"))
        else:
            if len(self.mapped('date')) > 0:
                user_options = self.env["res.users.options"].search([
                    ('user_id', '=', self.env.user.id)
                ])
                if user_options:
                    user_options.write({
                        "data_entry_date": max(self.mapped('date')) + timedelta(days=1),
                    })

            return super(AccountAnalyticLine, self).write(vals)

    def _default_project_id(self):
       try:
         self.default_project_id = self.default_get([])['project_id'].id
       except:
         self.default_project_id = False
       return

    def _default_task_id(self):
       try:
          self.default_task_id = self.default_get([])['task_id'].id
       except:
          self.default_task_id = False
       return

    def _default_date(self):
       try:
          self.default_date = self.default_get([])['date']
       except:
          self.default_date = False
       return

    def _default_employee_id(self):
        try:
          self.default_employee_id = self.default_get([])['employee_id']
        except:
          self.default_employee_id = False
        return


    def _default_work_type_id(self):
        try:
          self.default_work_type_id = self.default_get([])['work_type_id']
        except:
          self.default_work_type_id = False
        return


    def _default_unit_amount(self):
        try:
           self.default_unit_amount = self.default_get([])['unit_amount']
        except:
           self.default_unit_amount = False
        return

    @api.depends('work_type_id')
    def _compute_work_type_code(self):
        for rec in self:
            rec.work_type_code = rec.work_type_id.code

    @api.depends('worked_days_ids')
    # timesheet item spent in payroll
    def _calc_in_payroll(self):
        for rec in self:
            if rec.worked_days_ids:
                rec.in_payroll = rec.worked_days_ids[0].payslip_id.date_to
            else:
                rec.in_payroll = False

    def unlink(self):
        for rec in self:
            if rec.in_payroll:
                raise(ValidationError("Šihtarica iskorištena u obračunu se ne može brisati!"))
        return super(AccountAnalyticLine, self).unlink()


    def split_as_needed(self, hours_to_spend, food_days_rest):
        amount_to_split = self.unit_amount
        name_to_split = self.name.strip()
        work_type_id_1 = self.work_type_id
        work_type_old = work_type_id_1

        if work_type_id_1.code == '70_T':
            # stavka tipa '70_T' je vec podjeljena
            return True

        if work_type_old.food_included:
            env_db_work_type = self.env['hr.timesheet.work_type']
            # 10_SF => 11_S, 20_NF => 21_N, 30_WF => 31_W, 40_XF => 41_X
            if work_type_old.code == "10_SF":
                work_type_no_food = env_db_work_type.search([("code", '=', '11_S')])
            elif work_type_old.code == "20_NF":
                work_type_no_food = env_db_work_type.search([("code", '=', '21_N')])
            elif work_type_old.code == "30_WF":
                work_type_no_food = env_db_work_type.search([("code", '=', '31_W')])
            elif work_type_old.code == "40_XF":
                work_type_no_food = env_db_work_type.search([("code", '=', '41_X')])
            elif work_type_old.code == "80_SF":
                work_type_no_food = env_db_work_type.search([("code", '=', '81_S')])
            elif work_type_old.code == "90_SNF":
                work_type_no_food = env_db_work_type.search([("code", '=', '91_SN')])
            elif work_type_old.code == "A0_SDF":
                work_type_no_food = env_db_work_type.search([("code", '=', 'A1_SD')])
            elif work_type_old.code == "B0_SNDF":
                work_type_no_food = env_db_work_type.search([("code", '=', 'B1_SND')])
            else:
                raise(ValidationError('Način rada: ' + work_type_old.code + ' mora imati varijantu bez TO'))
        else:
            work_type_no_food = work_type_old

        # ostalo sati za potrositi ali je stavka prevelika pa treba napraviti split
        if hours_to_spend > 0 and hours_to_spend < amount_to_split:

            if food_days_rest <= 0:
                # we have reached food days limit
                work_type_id_1 = work_type_no_food  # potrošen mjesečni fond za TO: dijeli na stavku bez TO + stavka sa TO za preraspodjelu
                work_type_id_2 = work_type_old
            else:
                work_type_id_1 = work_type_old # nije potrošen mjesečni fond za TO: dijeli na stavku sa TO + stavka bez TO za preraspodjelu
                work_type_id_2 = work_type_no_food

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

            return True

        # sati nisu potroseni, stavka nije prevelika (broja sati se ne treba dijeliti), ali
        # smo potrosili fond sati za TO a stavka je sa TO ukljucenim
        elif hours_to_spend > 0 and hours_to_spend >= amount_to_split and food_days_rest == 0 and work_type_old.food_included:

            env_db_work_type = self.env['hr.timesheet.work_type']
            work_type_only_food = env_db_work_type.search([("code", '=', '70_T')])

            self.write({
                'unit_amount': amount_to_split,
                'name': 'splitTO-1: ' + name_to_split,
                'work_type_id': work_type_no_food.id
            })
            self.copy({
                'unit_amount': 0,
                'name': 'splitTO-2: ' + name_to_split,
                'work_type_id': work_type_only_food.id
            })

            return True

        # sati su potroseni ali dani za TO nisu i ova stavka je stavka sa TO
        elif hours_to_spend <= 0 and food_days_rest > 0 and work_type_old.food_included:

            # ostalo je dana TO = 3 dana, mjesecni fond sati = 0h, stavka Redovni rad sa TO (10_SF) = 5h
            # dijelimo je na stavke:
            # a) 70_T = 1
            # b) Redovni rad bez TO (11_S) = 5h za preraspodjelu 
            env_db_work_type = self.env['hr.timesheet.work_type']
            work_type_only_food = env_db_work_type.search([("code", '=', '70_T')])

            self.write({
                    'unit_amount': 0,
                    'name': 'splitTO1: ' + name_to_split,
                    'work_type_id': work_type_only_food.id
            })
            self.copy({
                'unit_amount': amount_to_split,
                'name': 'splitTO2: ' + name_to_split,
                'work_type_id': work_type_no_food.id
            })

            return True

        return False


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


    def _search_in_payroll(self, operator, value):
        if operator == '=':
           recs = self.search([]).filtered(lambda x: x.in_payroll == value)
        elif operator == '!=':
           recs = self.search([]).filtered(lambda x: x.in_payroll != value)
        else:
           # npr '@' - sadrzi
           #recs = self.search([]).filtered(lambda x: x.email and value in x.email)
           recs = []
        return [('id', 'in', [x.id for x in recs])]

