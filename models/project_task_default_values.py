from odoo import fields, models, api


class UserTimesheetOptionsWizard(models.TransientModel):
    _name = "user.timesheet.options.wizard"

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
        string="Tekući način rada",
        comodel_name="hr.timesheet.work_type"
    )
    data_entry_unit_amount = fields.Float(
        string="Tekući broj sati",
        default=8.0
    )           

    @api.model
    def default_get(self, fields):
        values = super().default_get(fields)
        #context = self.env.context
        #if context.get("active_model") == "f18.backend" and context.get("active_id"):
        #    backend = self.env["f18.backend"].browse(context["active_id"])
        user_options = self.env["res.users.options"].search([
            ('user_id', '=', self.env.user.id)
        ])
        
        if user_options:
            values.update({
                "data_entry_project_id": user_options.data_entry_project_id,
                "data_entry_task_id": user_options.data_entry_task_id,        
                "data_entry_date": user_options.data_entry_date,
                "data_entry_employee_id": user_options.data_entry_employee_id,
                "data_entry_work_type_id": user_options.data_entry_work_type_id,
                "data_entry_unit_amount": user_options.data_entry_unit_amount
            })
        return values

    def set_default_user_timesheet_options(self):

        user_options = self.env["res.users.options"].search([
            ('user_id', '=', self.env.user.id)
        ])

        record = {
            "data_entry_project_id": self.data_entry_project_id,
            "data_entry_task_id": self.data_entry_task_id,
            "data_entry_date": self.data_entry_date,
            "data_entry_employee_id": self.data_entry_employee_id,
            "data_entry_work_type_id": self.data_entry_work_type_id,
            "data_entry_unit_amount": self.data_entry_unit_amount,
        }

        if not user_options.create_date:
           user_options = self.env["res.users.options"].create(vals_list={})

        user_options.write(record)





