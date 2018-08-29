
var payWithRave = function(){
	var x = {
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
        onclose: function() {},
        callback: function(response) {
        	console.log(response)
			rave.make_payment_log(response, "{{ reference_doctype }}", "{{ reference_docname }}", "{{ token }}");
            //x.close(); // use this to close the modal immediately after payment.
        }
    };
    getpaidSetup(x);
};

$(document).ready(function(){
	payWithRave()
})

frappe.provide('rave');

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
