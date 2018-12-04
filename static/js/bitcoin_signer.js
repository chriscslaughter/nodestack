//var bitcoinjs = require('bitcoinjsjs-lib')


// var tx = bitcoinjs.Transaction.fromHex(txHex)

// transaction fromhex take rpc hex
// create transaction
// transactionbuilder.fromtransaction(transaction already built)
// tb.sign()
// tb.build().hex()

function doSigning() {
	console.log('here');
	let privateKey = document.getElementById('private_key').value;
	console.log(privateKey);
	var keyPair = bitcoinjs.ECPair.fromWIF(privateKey, bitcoinjs.networks.testnet)
	t = bitcoinjs.Transaction.fromHex(document.getElementById('transaction_current').value)
	tb = bitcoinjs.TransactionBuilder.fromTransaction(t, bitcoinjs.networks.testnet);
	//TODO: dynamically provide
	redeemScript = new bitcoinjs.buffer.Buffer('5221024abd86ffc298032b0af5a4c9adbfc7bd9a0aa5f1b4e7ecf01375f4d4cf79353921025c95cb6d0e4444c03bd20a2362ef6aa721ae2547a65aa53e0d9dfbe31c7bac7b210348877ca5abd8ee512b85d45746fed05bdfe715e7af4706e0417b33b1a254bcc453ae', 'hex')

	tb.sign(0, keyPair, redeemScript);
	document.getElementById('transaction_result').value = tb.build().toHex();
}
