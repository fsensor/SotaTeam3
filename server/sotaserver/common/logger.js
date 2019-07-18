'use strict';

const util = require('util');
const signer = require('./cryptoutil.js');
const baselogger = require('./baselogger.js');
const db = require('../storage/db.js');

function log(level, ...args) {
  if (args.length === 0 || level.gt(baselogger.getCurrentLogLevel())) {
    return;
  }
  let message = util.format(...args);
  db.getKey( key => {
    if (typeof key === 'undefined' || key === null) {
        baselogger.log(level, message + "  SIGN [Can't sign]");
    } else {
      signer.sign(message, key, signature => {
        baselogger.log(level, message + '  SIGN [' + signature + ']');
      });
    }
  });
}

function setLogLevel(level) {
  baselogger.setLogLevel(level);
}

var logger = {
  log: function (...args) {
    log(baselogger.LEVEL.I, ...args);
  },
  info: function (...args) {
    log(baselogger.LEVEL.I, ...args);
  },
  debug: function (...args) {
    log(baselogger.LEVEL.D, ...args);
  },
  warm: function (...args) {
    log(baselogger.LEVEL.W, ...args);
  },
  error: function (...args) {
    log(baselogger.LEVEL.E, ...args);
  },
  setLogLevel: setLogLevel,
};

baselogger.setConsole(console);
console = logger;

module.exports = {
  log: logger.log,
  info: logger.info,
  warn: logger.warn,
  error: logger.error,
  debug: logger.debug, 
  setLogLevel: setLogLevel,
  LEVEL: baselogger.LEVEL 
};
