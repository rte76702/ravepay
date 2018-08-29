# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt
from __future__ import unicode_literals
import frappe, json
from frappe import _
from frappe.utils import flt, cint
from six import string_types

no_cache = 1
no_sitemap = 1

expected_keys = ('amount', 'reference_doctype', 'reference_docname',
	'payer_phone', 'payer_email', 'txref', 'currency')

def get_context(context):
	ravedoc = frappe.get_doc("Rave Settings")
	context.url = 'ravesandboxapi.flutterwave.com' if \
						cint(ravedoc.test) else 'api.ravepay.co'
	try:
		context.no_cache = 1
		context.public_key = ravedoc.get_settings().public
		doc = frappe.get_doc("Integration Request", frappe.form_dict['token'])
		payment_details = json.loads(doc.data)
		if doc.status in ['Authorized', 'Completed', 'Failed']:
			frappe.throw('Invalid Token')

		for key in expected_keys:
			context[key] = payment_details.get(key)

		context['token'] = frappe.form_dict['token']
		context['amount'] = flt(context['amount'])

	except Exception:
		frappe.log_error(frappe.get_traceback(), 'get_context')
		frappe.redirect_to_message(_('Invalid Token'),
			_('Seems token you are using is invalid!'),
			http_status_code=400, indicator_color='red')

		frappe.local.flags.redirect_location = frappe.local.response.location
		raise frappe.Redirect


@frappe.whitelist(allow_guest=True)
def make_payment(txref, reference_doctype, reference_docname, token):
	data = {
		"txref": txref,
		"reference_docname": reference_docname,
		"reference_doctype": reference_doctype,
		"token": token
	}

	data =  frappe.get_doc("Rave Settings").create_request(data)
	frappe.db.commit()
	return data
