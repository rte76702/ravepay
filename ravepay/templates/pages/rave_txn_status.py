
import frappe, json


no_cache = 1
no_sitemap = 1

def get_context(context):
	context.title = 'Transaction Status'
	try:
		no_cache = 1
	
		if frappe.db.exists('Integration Request', frappe.form_dict.token):
			integration_request = frappe.db.get_value('Integration Request',
							frappe.form_dict.token, ['status', 'data'], as_dict=1)
			txn_data = json.loads(integration_request.data)
			context.txn_reference = txn_data['txref']
			context.txn_status = integration_request.status
		else:
			context.txn_status = 'Invalid Token'
			context.txn_reference = '--'
	except Exception:
		context.txn_status = 'Error'
		context.txn_reference = '--'
		frappe.log_error(frappe.get_traceback(), 'rave-txn-status')