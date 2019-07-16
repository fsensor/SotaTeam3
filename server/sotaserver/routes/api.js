var express = require('express');
var handler = require('../api/handler.js');
var router = express.Router();
var logger = require('../common/logger.js');

const ERROR_CODES = require('../common/errorcodes.js');

const ERRCODE_TO_STATUS = (function () {
  let mapping = new Map();
  mapping.set(ERROR_CODES.SUCCESS, 200);
  mapping.set(ERROR_CODES.ERR_NONE, 200);
  mapping.set(ERROR_CODES.ERR_UNKNOWN, 500);
  mapping.set(ERROR_CODES.ERR_INTERNAL_ERROR, 500);
  mapping.set(ERROR_CODES.ERR_INVALID_PARAMS, 400);
  mapping.set(ERROR_CODES.ERR_DB_INVALID_ID, 400);
  mapping.set(ERROR_CODES.ERR_DB_INVALID_ITEM, 400);
  mapping.set(ERROR_CODES.ERR_DB_INVALID_QUERY, 400);
  mapping.set(ERROR_CODES.ERR_DB_ONE_MATCH_REQUIRED, 400);
  mapping.set(ERROR_CODES.ERR_DB_INVALID_CATEGORY, 400);
  return mapping;
}());

function convertStatusCode(errorCode) {
  if (ERRCODE_TO_STATUS.has(errorCode)) {
    return ERRCODE_TO_STATUS.get(errorCode);
  }
  return 500;
}

function getFromErrorCode(errorCodes) {
  var response = {};
  response.result = ERROR_CODES.IsNoError(errorCodes) ? "success" : "failure";
  if (ERROR_CODES.IsError(errorCodes)) {
    response.error_details = errorCodes.toString();
  }

  return response;
}

function IsReqInvalid(req) {
  return (typeof req === 'undefined' || req === null || 
      typeof req.method  !== 'string' || typeof req.url !== 'string' ||
      typeof req.client === 'undefined' || req.client === null ||
      typeof req.client._peername === 'undefined' ||
      typeof req.socket === 'undefined' || req.socket === null ||
      typeof req.socket.server === 'undefined' || req.socket.server === null ||
      typeof req.socket.server.sessionIdContext === 'undefined');
}

function logRequest(req) {
  if (IsReqInvalid(req)) {
    console.log("REQ error");
    return null;
  }

  let reqinfo = req.method + " for " + req.url +
      " from " + JSON.stringify(req.client._peername) +
      " ID [" + req.socket.server.sessionIdContext +"]";

  logger.info("Request " + reqinfo);
  
  return reqinfo;
}

function logResponse(res, req) {
  if (typeof res === 'undefined' || res === null) {
    return;
  }

  logger.info("Response " + res.statusCode + " for the request " + req);
}

function getResultHandler(res, reqinfo) {
  return function (errorCode, result) {
    res.status(convertStatusCode(errorCode));
    if (ERROR_CODES.IsNoError(errorCode) && typeof result !== 'undefined') {
      res.json(result);
    } else {
      res.json(getFromErrorCode(errorCode));
    }
    logResponse(res, reqinfo);  
  };
}

router.options('*', (req, res, next) => {
		res.set('X-XSS-Protection', '1; mode=block');
		res.set('X-Frame-Options', "deny");
		res.set('Contetn-Security-Policy', "default-src 'self'");
		res.send();
});


router.get('/GetVersion', function(req, res, next) {
	handler.getVersion(getResultHandler(res, logRequest(req)));
});

router.get('/GetLatestImage', function(req, res, next) {
	handler.getLatestImage(getResultHandler(res, logRequest(req)));
});

module.exports = router;
