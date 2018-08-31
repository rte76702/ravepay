# -*- coding: utf-8 -*-
# Copyright (c) 2018, rte76702 and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import frappe, json, requests
from frappe import _
from frappe.model.document import Document
from frappe.utils import get_url, call_hook_method, cint, flt
from frappe.integrations.utils import create_request_log, create_payment_gateway

class RaveSettings(Document):
	supported_currencies = ["NGN"]

	def validate(self):
		if self.enable:
			create_payment_gateway('Rave')
			call_hook_method('payment_gateway_enabled', gateway='Rave')
			self.enabled = 1
			self.enable = None
			frappe.msgprint('Gateway Enabled')
		if self.disable:
			delete_payment_gateway('Rave')
			self.enabled = None
			self.disable = None
			frappe.msgprint('Gateway Disabled')

	def validate_transaction_currency(self, currency):
		if currency not in self.supported_currencies:
			frappe.throw(_("Please select another payment method. Rave does not support transactions in currency '{0}'").format(currency))

	def get_payment_url(self, **kwargs):
		kwargs.setdefault('currency', 'NGN')
		kwargs['txref'] = 'rave-'+frappe.generate_hash(length=15)
		integration_request = create_request_log(kwargs, "Host", "Rave")
		return get_url("./rave_checkout?token={0}".format(integration_request.name))

	def create_request(self, data):
		self.data = frappe._dict(data)
		try:
			self.integration_request = frappe.get_doc("Integration Request", self.data.token)
			self.integration_request.update_status(self.data, 'Queued')
			return self.authorize_payment()
		except Exception:
			frappe.log_error(frappe.get_traceback())
			return{
				"redirect_to": frappe.redirect_to_message(_('Server Error'), _("An Error Occurred While Processing Your Request.")),
				"status": 401
			}

	def authorize_payment(self):
		"""Verify Payments"""
		data = self.make_obj(json.loads(self.integration_request.data))
		settings = self.get_settings()

		try:
			url_host = 'ravesandboxapi.flutterwave.com' if cint(self.test) else 'api.ravepay.co'
			url = 'https://%s/flwv3-pug/getpaidx/api/v2/verify'%url_host
			req_data = {"txref": self.data.txref,"SECKEY": settings.secret}
			r = requests.post(url, req_data)
			resp = self.make_obj(r.json())

			if resp.data.chargecode in ['0','00'] and flt(resp.data.amount) == flt(data.amount):
				self.integration_request.update_status(data, 'Authorized')
				self.flags.status_changed_to = "Authorized"
			else:
				frappe.log_error(str(resp), 'Rave Payment not authorized')

		except:
			frappe.log_error(frappe.get_traceback())
			pass

		if self.flags.status_changed_to == "Authorized":
			if self.data.reference_doctype and self.data.reference_docname:
				try:
					ref_doc = frappe.get_doc(self.data.reference_doctype,self.data.reference_docname)
					ref_doc.run_method("on_payment_authorized", self.flags.status_changed_to)
				except Exception:
					frappe.log_error(frappe.get_traceback())

		return {"redirect_to": '/rave-txn-status?token=%s'%self.integration_request.name}

	def get_settings(self):
		settings = frappe._dict({
			"public": self.get_password(fieldname="public_key", raise_exception=False),
			"secret": self.get_password(fieldname="secret_key", raise_exception=False)
		})

		return settings

	def make_obj(self, data): 
		nd = frappe._dict(data)
		for key in nd:         
			if isinstance(nd[key], dict):
				nd[key] = self.make_obj(nd[key])
		return nd

def delete_payment_gateway(gateway):
	frappe.db.sql("delete from `tabPayment Gateway` where \
					gateway = '%s'"%gateway, auto_commit=1)