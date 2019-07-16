'use strict';

const crypto = require('crypto');
const db = require('../storage/db.js');
const hash_algorithm = 'SHA256';

function sign(message) {
  if (typeof message !== 'string') {
    return;
  }
  
  let sign = crypto.createSign(hash_algorithm);

  sign.update(message);
  sign.end();
  
  let signature = sign.sign(db.getKey(), 'hex');
  
  return signature;
}

function verify(message, signature)
{
  if (typeof message !== 'string' || typeof signature !== 'string') {
    return false;
  }

  let verify = crypto.createVerify(hash_algorithm);
  verify.update(message);
  verify.end();
  return verify.verify(db.getCert(), signature, 'hex');
}

module.exports = {
  sign: sign,
  verify: verify
}

