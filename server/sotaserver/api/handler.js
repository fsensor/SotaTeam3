'use strict';

var db = require('../storage/db.js');
var imagereader= require('../storage/imagereader.js');
var asynccaller = require('../common/asynccaller.js');
var signer = require('../common/cryptoutil.js');

const logger = require('../common/logger.js');
const ERROR_CODES = require('../common/errorcodes.js');

function getLatestValue(meta, index) {
  if (typeof index !== 'string') {
    return null;
  }

  let latest = 0;
  let latestvalue = null;
  logger.info(meta); 
  for (let version of meta) {
    let verstr = version["version"]; 
    if (typeof verstr !== 'string') {
      continue;
    }
    let vernum = Number.parseInt(verstr.replace(/\./g, ''), 10);
    if (vernum !== NaN && vernum > latest) {
      latest = vernum;
      latestvalue = version[index];
    }
  }
	return latestvalue;
}

function getLatestVersion(meta) {
  return getLatestValue(meta, "version");
}

function getLatestPath(meta) {
  return getLatestValue(meta, "path");
}

function getVersion(onResult) {
	if (typeof onResult === 'function') {
		db.getImageMetas((errorcode, meta) => {
			if (ERROR_CODES.IsNoError(errorcode)) {
        let latestversion = getLatestVersion(meta);
        if (latestversion !== null) {
          signer.sign(latestversion, signature => {
            asynccaller.call(
              onResult,
              errorcode,
              { version: latestversion, sign: signature }
            );
          });
          return;
        } 
        logger.error("No latest version");        
        errorcode = ERROR_CODES.ERR_INTERNAL_ERROR;
			} else { 
        logger.error("No meta data for images");        
      }
			asynccaller.call(onResult, errorcode, null);
		});
	}
}

function getLatestImage(onResult) {
	if (typeof onResult === 'function') {
		db.getImageMetas((errorcode, meta) => {
			if (ERROR_CODES.IsNoError(errorcode)) {
        let path = getLatestPath(meta);

        if (path === null) {
				  asynccaller.call(onResult, ERROR_CODES.ERR_INTERNAL_ERROR, null);
          return;
        }

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
