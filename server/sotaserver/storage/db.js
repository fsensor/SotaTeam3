'use strict';

var fs = require("fs");
var asynccaller = require('../common/asynccaller.js');

const ImageMeta = require('../models/imageMeta');

// CONNECT TO MONGODB SERVER
var mongoose = require('mongoose');
var db = mongoose.connection;
db.on('error', console.error);
db.once('open', function(){
    // CONNECTED TO MONGODB SERVER
    console.log("Connected to mongod server");
});
mongoose.connect('mongodb://localhost/imageMeta', { useNewUrlParser: true });

const ERROR_CODES = require('../common/errorcodes.js');

function getKeyByType(onResult, type) {
  if (typeof type !== 'string') {
    asynccaller.call(onResult, null);
    return;
  }

	ImageMeta.certificate.find(
      (err, meta) => {
        let key = null;
        if (!err) {
          key=fs.readFileSync(meta[0][type]);
        }
        asynccaller.call(onResult, key);
      }
  );
}

function getCert(onResult) {
  if (typeof onResult !== 'function') {
    return;
  }
  
  getKeyByType(onResult, "cert");
}

function getKey(onResult) {
  if (typeof onResult !== 'function') {
    return;
  }
  
  getKeyByType(onResult, "key");
}

function getCACert(onResult) {
  if (typeof onResult !== 'function') {
    return;
  }
  
  getKeyByType(onResult, "cacert");
}

function getImageMetas(onResult) {
	if (typeof onResult !== 'function') {
		return;
	}

	// TODO: Read from real db
  console.log("Access to DB to get image meta data");
	ImageMeta.version.find(function(err, meta) {
    let errorcode = ERROR_CODES.SUCCESS;

		if (err) {
      console.log("DB read error");
      errorcode = ERROR_CODE.ERR_INTERNAL_ERROR;
		} 

    asynccaller.call(
				onResult,
				errorcode,
			  meta	
			);
	});
}

module.exports = {
	getCert: getCert,
	getCACert : getCACert,
	getKey: getKey,
	getImageMetas: getImageMetas
}
