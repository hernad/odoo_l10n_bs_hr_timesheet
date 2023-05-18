# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

# Author: Ernad Husremovic
# mail:   hernad@bring.out.ba
{
    "name": "Bosnia and Herzegovina Timesheets",
    "description": """
Bosnian localisation.
======================

Author: Ernad Husremovic bring.out doo Sarajevo

Description:

Bosnian timesheet work types

""",
    "version": "16.0.5",
    "author": "bring.out",
    'category': 'Timesheet',
    "website": "https://github.com/hernad/odoo",
    'depends': ['base', 'hr_timesheet'],
    'data': [
        'data/work_types_data.xml',
        'security/ir.model.access.csv',
        'views/work_type.xml',
        'views/user_timesheet_options.xml'
    ],
    "active": False,
    'license': 'GPL-3',
}
