var bitcoin = require('bitcoinjs-lib');
var testnet = bitcoin.networks.testnet;

var keyPairs = [
	'cSB1o7v1QBZDHJropQqBYfuiUA4Js1o24uzkgB2vYeND1st5uGqV',
	'cU3C1Uu4oN8ZPXrCz55GyjmrsaeoF8UhmBai2d9jzq9iw7ty9EMc'
].map(function(xpriv) {
	return bitcoin.ECPair.fromWIF(xpriv, testnet);
});

var pubKeys = keyPairs.map(function (xpub) { return xpub.publickey });

var witnessScript = bitcoin.script.multisig.output.encode(2, pubKeys)
var witnessScriptHash = bitcoin.crypto.sha256(witnessScript)

var redeemScript = bitcoin.script.witnessScriptHash.output.encode(witnessScriptHash)
var redeemScriptHash = bitcoin.crypto.hash160(redeemScript)
var scriptPubKey = bitcoin.script.scriptHash.output.encode(redeemScriptHash)
var address = bitcoin.address.fromOutputScript(scriptPubKey, testnet)

console.log(address);

var txb = new bitcoin.TransactionBuilder(testnet)
txb.addInput('e58216a8ccf3e1b7c892dd6afee0d86435c28cbf25fc210c99c60a7aee9dadbc', 1)
txb.addOutput(address, 150000)
txb.sign(0, keyPairs[0], redeemScript, null, 200000, witnessScript)
txb.sign(0, keyPairs[1], redeemScript, null, 200000, witnessScript)

var tx = txb.build()
var txid = tx.getId()
var txhex = tx.toHex();

console.log(txid);
console.log(txhex);
