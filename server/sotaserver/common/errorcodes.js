module.exports = (function () {
  var errorCodes = {};

  errorCodes.SUCCESS = new Number(0x00);
  errorCodes.SUCCESS.toString = function() {
    return 'Success';
  };
  errorCodes.ERR_NONE = errorCodes.SUCCESS;

  // Common errors
  errorCodes.ERR_UNKNOWN = new Number(0x03);
  errorCodes.ERR_UNKNOWN.toString = function() {
    return 'Unknown error';
  };

  errorCodes.ERR_INTERNAL_ERROR = new Number(0x03);
  errorCodes.ERR_INTERNAL_ERROR.toString = function() {
    return 'Internal error';
  };

  errorCodes.ERR_INVALID_PARAMS = new Number(0x04);
  errorCodes.ERR_INVALID_PARAMS.toString = function() {
    return 'Invalid parameters';
  };

  errorCodes.IsNoError = function (code) {
    return (code === errorCodes.SUCCESS);
  };

  errorCodes.IsError = function (code) {
    return (code !== errorCodes.SUCCESS);
  };

  return errorCodes;
}());
