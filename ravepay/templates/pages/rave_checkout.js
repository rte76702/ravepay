

frappe.provide('rave');

$(document).ready(function(){
	payWithRave()
})

function payWithRave(){
	try {
		var x = getpaidSetup({
			PBFPubKey: "{{ public_key }}",
			customer_email: "{{ payer_email }}",
			amount: cint("{{ amount }}"),
			customer_phone: "{{ payer_phone }}",
	        currency: "{{ currency }}",
	        payment_method: "both",
	        txref: "{{ txref }}",
	        meta: [{
	            metaname: "{{ reference_doctype }}",
	            metavalue: "{{ reference_docname }}"
	        }],
	        onclose: function() {
	        	if (!rave.payment_callback) {
	        		rave.make_payment_log(response, "{{ reference_doctype }}", "{{ reference_docname }}", "{{ token }}");
	        	}
	        },
	        callback: function(response) {
	        	rave.payment_callback = 1
	            x.close(); // use this to close the modal immediately after payment.
				rave.make_payment_log(response, "{{ reference_doctype }}", "{{ reference_docname }}", "{{ token }}");
	        }
	    });
	} catch (e) {
		rave.make_payment_log(response, "{{ reference_doctype }}", "{{ reference_docname }}", "{{ token }}");
	}
};



rave.make_payment_log = function(response, doctype, docname, token){
	$('.rave-loading').addClass('hidden');
	$('.rave-confirming').removeClass('hidden');

	frappe.call({
		method:"ravepay.templates.pages.rave_checkout.make_payment",
		freeze:true,
		headers: {"X-Requested-With": "XMLHttpRequest"},
		args: {
			"txref": response.data.tx.txRef,
			"reference_doctype": doctype,
			"reference_docname": docname,
			"token": token
		},
		callback: function(r){
			if (r.message.redirect_to) {
				window.location.href = r.message.redirect_to
			}
		}
	})
}
