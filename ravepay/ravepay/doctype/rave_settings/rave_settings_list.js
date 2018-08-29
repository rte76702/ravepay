
frappe.listview_settings['Rave Settings'] = {
	add_fields: ["enabled"],
	get_indicator: function(doc) {
		return (cint(doc.enabled) ? ['Enabled', "green"] : ['Disabled', "grey"]);
	}
};
