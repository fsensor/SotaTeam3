'use strict';

const crypto = require('crypto');
const asynccaller = require('./asynccaller.js');
const db = require('../storage/db.js');
const hash_algorithm = 'SHA256';

function sign(message, onResult) {
  if (typeof message !== 'string' ||
      typeof onResult !== 'function') {
    return;
  }
  
  let sign = crypto.createSign(hash_algorithm);

  sign.update(message);
  sign.end();
  db.getKey(key => {
    let signature = null;
    if (key !== null) {
      signature = sign.sign(key, 'hex');
    }
    asynccaller.call(onResult, signature);
  });
}

function verify(message, signature, onResult)
{
  if (typeof message !== 'string' ||
      typeof signature !== 'string' ||
      typeof onResult !== 'function') {
    return false;
  }

  let verify = crypto.createVerify(hash_algorithm);
  verify.update(message);
  verify.end();
  db.getCert(cert => {
    let result = false;
    if (cert !== null) {
      result = verify.verify(cert, signature, 'hex')
    }
    asynccaller.call(onResult, result);
  })
  return ;
}

module.exports = {
  sign: sign,
  verify: verify
}

