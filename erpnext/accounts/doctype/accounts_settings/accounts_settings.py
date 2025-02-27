# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

# For license information, please see license.txt


import frappe
from frappe import _
from frappe.custom.doctype.property_setter.property_setter import make_property_setter
from frappe.model.document import Document
from frappe.utils import cint


class AccountsSettings(Document):
	def on_update(self):
		frappe.clear_cache()

	def validate(self):
		frappe.db.set_default("add_taxes_from_item_tax_template",
			self.get("add_taxes_from_item_tax_template", 0))

		self.validate_stale_days()
		self.enable_payment_schedule_in_print()
		self.toggle_discount_accounting_fields()

	def validate_stale_days(self):
		if not self.allow_stale and cint(self.stale_days) <= 0:
			frappe.msgprint(
				_("Stale Days should start from 1."), title='Error', indicator='red',
				raise_exception=1)

	def enable_payment_schedule_in_print(self):
		show_in_print = cint(self.show_payment_schedule_in_print)
		for doctype in ("Sales Order", "Sales Invoice", "Purchase Order", "Purchase Invoice"):
			make_property_setter(doctype, "due_date", "print_hide", show_in_print, "Check", validate_fields_for_doctype=False)
			make_property_setter(doctype, "payment_schedule", "print_hide",  0 if show_in_print else 1, "Check", validate_fields_for_doctype=False)

	def toggle_discount_accounting_fields(self):
		enable_discount_accounting = cint(self.enable_discount_accounting)

		for doctype in ["Sales Invoice Item", "Purchase Invoice Item"]:
			make_property_setter(doctype, "discount_account", "hidden", not(enable_discount_accounting), "Check", validate_fields_for_doctype=False)
			if enable_discount_accounting:
				make_property_setter(doctype, "discount_account", "mandatory_depends_on", "eval: doc.discount_amount", "Code", validate_fields_for_doctype=False)
			else:
				make_property_setter(doctype, "discount_account", "mandatory_depends_on", "", "Code", validate_fields_for_doctype=False)

		for doctype in ["Sales Invoice", "Purchase Invoice"]:
			make_property_setter(doctype, "additional_discount_account", "hidden", not(enable_discount_accounting), "Check", validate_fields_for_doctype=False)
			if enable_discount_accounting:
				make_property_setter(doctype, "additional_discount_account", "mandatory_depends_on", "eval: doc.discount_amount", "Code", validate_fields_for_doctype=False)
			else:
				make_property_setter(doctype, "additional_discount_account", "mandatory_depends_on", "", "Code", validate_fields_for_doctype=False)

		make_property_setter("Item", "default_discount_account", "hidden", not(enable_discount_accounting), "Check", validate_fields_for_doctype=False)
