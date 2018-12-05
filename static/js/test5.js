var bitcoin = require('bitcoinjs-lib')


// var tx = bitcoin.Transaction.fromHex(txHex)

// transaction fromhex take rpc hex
// create transaction
// transactionbuilder.fromtransaction(transaction already built)
// tb.sign()
// tb.build().hex()


let privateKey = 'cRP9kZKKw4zmqE4M2sD9zS4LKroJ79yHnCv8LX5RXWEavxSFH9Mn'
var keyPair = bitcoin.ECPair.fromWIF(privateKey, bitcoin.networks.testnet)

let privateKey2 = 'cSuHL8HCenz8Hen5ztHYhcsvwDmA45npB7qm1cU1CJaFXYiEMbob'
var keyPair2 = bitcoin.ECPair.fromWIF(privateKey2, bitcoin.networks.testnet)

t = bitcoin.Transaction.fromHex('0200000002740d01ced2866d666efb82278424f603de8962a12985ccebccfd478736cd263a0100000000ffffffffb5c6818707977b8caf47d6e13d400f79354e5cb38ad4e21522c373a77bc0a5ea0000000000ffffffff0200c2eb0b0000000017a9148afcccd57ad6a369af7754a61af24e68fb6404f48760ebd7a90000000017a914d1181abf9dc1860c5ed42f254f516597165a00fc8700000000')
tb = bitcoin.TransactionBuilder.fromTransaction(t, bitcoin.networks.testnet);

redeemScript = Buffer('5221024abd86ffc298032b0af5a4c9adbfc7bd9a0aa5f1b4e7ecf01375f4d4cf79353921025c95cb6d0e4444c03bd20a2362ef6aa721ae2547a65aa53e0d9dfbe31c7bac7b210348877ca5abd8ee512b85d45746fed05bdfe715e7af4706e0417b33b1a254bcc453ae', 'hex')

tb.sign(0, keyPair2, redeemScript);
tb.sign(1, keyPair2, redeemScript);
console.log(t);
t2 = tb.build();
console.log(t2.toHex());
