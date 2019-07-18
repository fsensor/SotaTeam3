'use strict';

const crypto = require('crypto');
const asynccaller = require('./asynccaller.js');
const db = require('../storage/db.js');
const hash_algorithm = 'SHA256';

function sign(message, key, onResult) {
  if (typeof message !== 'string' ||
      typeof key === 'undefined' || key === null ||
      typeof onResult !== 'function') {
    return;
  }
  
  let sign = crypto.createSign(hash_algorithm);

  sign.update(message);
  sign.end();

  asynccaller.call(onResult, sign.sign(key, 'hex'));
}

function verify(message, key, signature, onResult)
{
  if (typeof message !== 'string' ||
      typeof key === 'undefined' || key === null ||
      typeof signature !== 'string' ||
      typeof onResult !== 'function') {
    return false;
  }

  let verify = crypto.createVerify(hash_algorithm);
  verify.update(message);
  verify.end();
  asynccaller.call(onResult, verify.verify(key, signature, 'hex'));
  return ;
}

module.exports = {
  sign: sign,
  verify: verify
}

