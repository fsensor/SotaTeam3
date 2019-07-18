'use strict';

var fs = require("fs");
var asynccaller = require('../common/asynccaller.js');

const baselogger = require('../common/baselogger.js');
const signer = require('../common/cryptoutil.js');

const ERROR_CODES = require('../common/errorcodes.js');
const ImageMeta = require('../models/imageMeta');

// CONNECT TO MONGODB SERVER
var dbname='sotares';
var dbport='30718';

let cmdLineOptions = process.argv.slice(2);

for (let option of cmdLineOptions) {
  if (option.startsWith('dbp=')) {
    let port = Number.parseInt(option.replace('dbp=', ''));
    if (!Number.isNaN(port)) {
      dbport = port;
    }
  } else if (option.startsWith('dbn=')) {
    let database = option.replace('dbn=', '');
    if (database !== null && database.length !== 0) {
      dbname = database;
    }
  }
}

function doLogWithKey(level, key, message) {
  if (typeof key === 'undefined' || key === null) {
      baselogger.log(level, message + "  SIGN [can't sign]");
  } else {
    signer.sign(message, key, signature => {
      baselogger.log(level, message + '  SIGN [' + signature + ']');
    });
  }
}

var get_key=null;

function doLog(level, message) {
  get_key( key => {
    doLogWithKey(level, key, message);
  });
}


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
        asynccaller.call(
            () => {
              if (type === "key") {
                doLogWithKey(baselogger.LEVEL.I, key, "GET" + type + "from DB");
              } else {
                doLog(baselogger.LEVEL.I, "GET" + type + "from DB"); 
              }
              onResult(key);
            },
        );
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
  doLog("Access to DB to get image meta data");
	ImageMeta.version.find(function(err, meta) {
    let errorcode = ERROR_CODES.SUCCESS;

		if (err) {
      doLog("DB read error");
      errorcode = ERROR_CODE.ERR_INTERNAL_ERROR;
		} 

    asynccaller.call(
				onResult,
				errorcode,
			  meta	
			);
	});
}

function getClientFingerprints(onResult) {
	if (typeof onResult !== 'function') {
		return;
	}

	// TODO: Read from real db
  doLog("Access to DB to get clients' fingerprint");
	ImageMeta.fingerprint.find(function(err, meta) {
    let errorcode = ERROR_CODES.SUCCESS;

		if (err) {
      doLog("DB read error");
      errorcode = ERROR_CODE.ERR_INTERNAL_ERROR;
		} 

    asynccaller.call(
				onResult,
				errorcode,
			  meta	
			);
	});
}

get_key = getKey;
var mongoose = require('mongoose');
var db = mongoose.connection;
db.on('error', console.error);
db.once('open', function(){
    // CONNECTED TO MONGODB SERVER
    doLog(baselogger.LEVEL.I, "Connected to mongod server");
});

mongoose.connect(
    'mongodb://localhost:' + dbport + '/' + dbname,
    { useNewUrlParser: true }
);


module.exports = {
	getCert: getCert,
	getCACert : getCACert,
	getKey: getKey,
	getImageMetas: getImageMetas,
  getClientFingerprints: getClientFingerprints
}
