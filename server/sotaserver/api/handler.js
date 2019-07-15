'use strict';

var db = require('../storage/db.js');
var imagereader= require('../storage/imagereader.js');
var asynccaller = require('../common/asynccaller.js');

const ERROR_CODES = require('../common/errorcodes.js');

function convertVersionFormat(version) {
	// Using the same format right now.
	return version;
}

function getVersion(onResult) {
	if (typeof onResult === 'function') {
		db.getVersion((errorcode, version) => {
      if (ERROR_CODES.IsNoError(errorcode)) {
			  asynccaller.call(onResult, errorcode, convertVersionFormat(version));
      } else {
			  asynccaller.call(onResult, errorcode, null);
      }
		});
	}
}

function getLatestImage(onResult) {
	if (typeof onResult === 'function') {
		db.getLatestImagePath((errorcode, path) => {
      if (ERROR_CODES.IsNoError(errorcode)) {
        imagereader.readImage(
            (errorcode, image) => {
               asynccaller.call(onResult, errorcode, image);
            },
            path
        );
  
      } else {
			  asynccaller.call(onResult, errorcode, null);
      }
		});
	}
}

module.exports = {
	getVersion: getVersion,
	getLatestImage: getLatestImage
};
