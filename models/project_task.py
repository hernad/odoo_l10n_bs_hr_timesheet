from datetime import timedelta
from odoo import fields, models, api


class ProjectTaskTimeSheetBs(models.Model):
    _inherit = 'project.task'
    
    default_date = fields.Date(compute='_default_date', store=False)
    default_work_type_id = fields.Integer(compute='_default_work_type_id', store=False)
    default_unit_amount = fields.Float(compute='_default_unit_amount', store=False)
    default_employee_id = fields.Integer(compute='_default_employee_id', store=False)

    #timesheet_ids = fields.One2many('account.analytic.line', 'task_id', 'Timesheets')
    timesheet_new_ids = fields.One2many(
        comodel_name='account.analytic.line', 
        inverse_name='task_id',
        domain = [('write_date', '>', fields.Datetime.now() - timedelta(days=32) )],
        #domain=[('in_payroll','=',False)],
        string='Šihtarice unesene posljednjih 31 dan')

    @api.constrains('timesheet_ids')
    def _check_timesheet_unit_amount(self):
        for timesheet in self.timesheet_ids:
            if timesheet.unit_amount < 0.01:
                # stavke sa splitTO u nazivu su tipa 70_T (Topli obrok only)
                if  not 'splitTO' in timesheet.name:
                   raise ValidationError(_('Broj sati mora biti > 0'))
            if timesheet.unit_amount > 16:
                raise ValidationError(_('Broj sati mora biti <= 16'))

    @api.model
    def default_get(self, fields_list):

        values = super().default_get(fields_list)
        user_options = self.env["res.users.options"].search([
            ('user_id', '=', self.env.user.id)
        ])

        if user_options:
            values.update({        
                "date": user_options.data_entry_date,
                "employee_id": user_options.data_entry_employee_id,
                "work_type_id": user_options.data_entry_work_type_id,
                "unit_amount": user_options.data_entry_unit_amount
            })

        return values    

    def _default_date(self):
       if 'date' in self.default_get([]): 
          self.default_date = self.default_get([])['date']
       else:
          self.default_date = False
       return

    def _default_employee_id(self):
        if 'employee_id' in self.default_get([]):
           self.default_employee_id = self.default_get([])['employee_id']
        else:
           self.default_employee_id = False
        return


    def _default_work_type_id(self):
        if 'work_type_id' in self.default_get([]):
           self.default_work_type_id = self.default_get([])['work_type_id']
        else:
           self.default_work_type_id = False
        return


    def _default_unit_amount(self):
        if 'unit_amount' in self.default_get([]):
           self.default_unit_amount = self.default_get([])['unit_amount']
        else:
           self.default_unit_amount = False
        return

    def set_default_data_entry_values(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'user.timesheet.options.wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'views': [[False, 'form']],
            'target': 'new',
        }


    def write(self, vals):
        #if len(self.mapped('date')) > 0:
        #    user_options = self.env["res.users.options"].search([
        #         ('user_id', '=', self.env.user.id)
        #    ])
        #    if user_options:
        #          user_options.write({
        #                "data_entry_date": max(self.mapped('date')) + timedelta(days=1),
        #          })

        # vals['timesheet_ids'] = [[4,11726,False],...,
        #                          [0, 'virtual_4',
        #                          {'date': '2023-04-10', 'user_id': 2, 'employee_id': 339, 'name': '10', 'work_type_id': 1, 'unit_amount': 8,
        #                           'project_id': 20, 'task_id': False}],
        #                          [4, 19202, False], [4, 19203, False]]
        return super(ProjectTaskTimeSheetBs, self).write(vals)
