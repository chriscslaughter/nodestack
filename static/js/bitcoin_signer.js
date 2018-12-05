function doSigning() {
	let privateKey = django.jQuery('#private_key').val();
	var keyPair = bitcoinjs.ECPair.fromWIF(privateKey, bitcoinjs.networks.testnet)
	t = bitcoinjs.Transaction.fromHex(django.jQuery('#transaction_current').val())
	tb = bitcoinjs.TransactionBuilder.fromTransaction(t, bitcoinjs.networks.testnet);
	redeemScript = new bitcoinjs.buffer.Buffer(django.jQuery('.field-redeem_script .readonly')[0].innerHTML, 'hex')
	for(var i =0; i < t.ins.length; i++) {
		tb.sign(i, keyPair, redeemScript);
	}
	django.jQuery('#transaction_result').val(tb.build().toHex());
}
