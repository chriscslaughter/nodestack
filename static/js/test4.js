var bitcore = require('bitcore-lib');

var privateKeys = [
  new bitcore.PrivateKey('91avARGdfge8E4tZfYLoxeJ5sGBdNJQH4kvjJoQFacbgwmaKkrx'),
  new bitcore.PrivateKey('91avARGdfge8E4tZfYLoxeJ5sGBdNJQH4kvjJoQFacbgww7vXtT')
];
var publicKeys = privateKeys.map(bitcore.PublicKey);
var address = new bitcore.Address(publicKeys, 2); // 2 of 2

var utxo = {
  "txId" : "466220d89f00716a188806ef2b3e558dbead9dc6a600db0c93e22d893d87a7b8",
  "outputIndex" : 1,
  "address" : address.toString(),
  "script" : new bitcore.Script(address).toHex(),
  "satoshis" : 1649500000
};

var transaction = new bitcore.Transaction()
    .from(utxo, publicKeys, 2)
    .to('mtoKs9V381UAhUia3d7Vb9GNak8Qvmcsme', 1640000000)
    .sign(privateKeys);

console.log(transaction.serialize())
