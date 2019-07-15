var express = require('express');
var handler = require('../api/handler.js');
var router = express.Router();

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

function getResultHandler(res) {
  return function (errorCode, result) {
    res.status(convertStatusCode(errorCode));
    if (ERROR_CODES.IsNoError(errorCode) && typeof result !== 'undefined') {
      res.json(result);
    } else {
      res.json(getFromErrorCode(errorCode));
    }
  };
}

router.options('*', (req, res, next) => {
		res.set('X-XSS-Protection', '1; mode=block');
		res.set('X-Frame-Options', "deny");
		res.set('Contetn-Security-Policy', "default-src 'self'");
		res.send();
});

router.get('/GetVersion', function(req, res, next) {
	handler.getVersion(getResultHandler(res));
});

router.get('/GetLatestImage', function(req, res, next) {
	handler.getLatestImage(getResultHandler(res));
});

module.exports = router;
