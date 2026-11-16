{'name': "Silver Gym",
 'author': "Eng Karim Shawky",
 'category': "",
 'version': "18.0.0.1.0",
 'depends': [
     'base', 'hr', 'contacts', 'account', 'stock', 'point_of_sale','purchase'
 ],
 'data': [
     'security/ir.model.access.csv',
     # 'security/security.xml',
     'data/barcode_sequence.xml',
     'views/base_menu_view.xml',
     'views/membership_plans_view.xml',
     'views/subscribing_view.xml',
     # 'views/private_plan_view.xml',
     'views/gym_attendance_view.xml',
     'wizards/check_in_wizard.xml',
     # 'wizards/register_inbody_wizard.xml'
 ],
 'assets' : {
 }
 ,
 'license': 'LGPL-3',
 'application': True,
 }


