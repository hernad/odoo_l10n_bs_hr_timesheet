from odoo import fields, models

class UserOptions(models.Model):
    _name = 'res.users.options'

    user_id = fields.Many2one('res.users', string='Tekući user', default=lambda self: self.env.user)

    data_entry_project_id = fields.Many2one(string="Tekući projekat", comodel_name="project.project")
    data_entry_task_id = fields.Many2one(
        string="Tekući zadatak", 
        comodel_name="project.task",
        domain="[('project_id.allow_timesheets', '=', True),"
               "('project_id', '=?', data_entry_project_id)]"
    )    

    data_entry_date = fields.Date(string="Tekući datum")
    data_entry_employee_id = fields.Many2one(
        string="Tekući zaposlenik",
        comodel_name="hr.employee"
    )
    data_entry_work_type_id = fields.Many2one(
        string="Work Type",
        comodel_name="hr.timesheet.work_type"
    )
    data_entry_unit_amount = fields.Float(
        string="Unit amount",
        default=8.0
    )

