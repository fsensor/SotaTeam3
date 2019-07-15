'use strict';

var fs = require('fs');
var asynccaller = require('../common/asynccaller.js');

const ERROR_CODES = require('../common/errorcodes.js');

const ENCODING = {
  BASE64: 'base64'
};

function readImage(callback, path, encoding=ENCODING.BASE64) {
  if (typeof callback !== 'function') {
    return;
  }

  if ( typeof path !== 'string' ) {
    asynccaller.call(callback, ERROR_CODES.ERR_INVALID_PARAMS, null);
    return;
  }
  
  if (encoding !== ENCODING.BASE64) {
    asynccaller.call(callback, ERROR_CODES.ERR_INVALID_PARAMS, null);
    return;
  }
  
  // What should we check more? 
  // How to check this is really an image we support? 
  fs.readFile(path, encoding, (err, data) => {
    if (err) {
      console.log(err);
      asynccaller.call(callback, ERROR_CODES.ERR_INTERNAL_ERROR, null);
      return;
    }
    
    // Do we need to checksum or signature??  
    asynccaller.call(callback, ERROR_CODES.SUCCESS, data);
  }); 
}

module.exports = {
  readImage: readImage,
  ENCODING: ENCODING
};
