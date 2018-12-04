var bitcoin = require('bitcoinjs-lib')


// var tx = bitcoin.Transaction.fromHex(txHex)

// transaction fromhex take rpc hex
// create transaction
// transactionbuilder.fromtransaction(transaction already built)
// tb.sign()
// tb.build().hex()


let privateKey = 'cU3C1Uu4oN8ZPXrCz55GyjmrsaeoF8UhmBai2d9jzq9iw7ty9EMc'
var keyPair = bitcoin.ECPair.fromWIF(privateKey, bitcoin.networks.testnet)

let privateKey2 = 'cSB1o7v1QBZDHJropQqBYfuiUA4Js1o24uzkgB2vYeND1st5uGqV'
var keyPair2 = bitcoin.ECPair.fromWIF(privateKey2, bitcoin.networks.testnet)

t = bitcoin.Transaction.fromHex('0200000001b8a7873d892de2930cdb00a6c69dadbe8d553e2bef0688186a71009fd8206246010000009200483045022100a2a0476ac713fec6e4613130a59ca2f772f5ccd6f2246455b9dff7ae2c066cfc02202cc5a3afd255f1ee6aa9afe8555fddda408ab39acef817583cb3df4cd1734c2301475221032559b7054ff5468aa9508579379b62c5f6b31145e5bfe743fc66c0ec72608dab21030eaf6ea71e09bd6f6b10a3ee42cc1a445d9020627a4569f17b7fbf1d5801959a52aeffffffff028093dc140000000017a914a732060d1955ab93c50c1096597e2ea466b9937d8780d6e34c0000000017a9142d2aad185524b244ef2b2f6a0507d6f187d02fbe8700000000')
tb = bitcoin.TransactionBuilder.fromTransaction(t, bitcoin.networks.testnet);

redeemScript = Buffer('5221032559b7054ff5468aa9508579379b62c5f6b31145e5bfe743fc66c0ec72608dab21030eaf6ea71e09bd6f6b10a3ee42cc1a445d9020627a4569f17b7fbf1d5801959a52ae', 'hex')

//tb.sign(0, keyPair2, redeemScript);
tb.sign(0, keyPair, redeemScript);
console.log(t);
t2 = tb.build();
console.log(t2.toHex());
