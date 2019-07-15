'use strict';

const remote_admin = require("./remoteadmin.js");
const util = require("util");

var logger, 
  levels = {
    E: 0, W: 1, I: 2, D: 3,
  },
  currentLevel = levels.I,
  realConsole = console;

function logToRemoteAdmin(level, message) {
  remote_admin.sendMessage(
      remote_admin.TYPE.LOG,
      {level: level, message: message}
  );
}

function log(level, ...args) {
  if (args.length === 0 || level > currentLevel) {
    return;
  }

  realConsole.log(...args)
  logToRemoteAdmin(level, util.format(...args));
}

function setLogLevel(level) {
  if (typeof level !== 'number') {
    return;
  }
  currentLevel = level;
}

logger = {
  log: function (...args) {
    log(levels.I, ...args);
  },
  info: function (...args) {
    log(levels.I, ...args);
  },
  debug: function (...args) {
    log(levels.D, ...args);
  },
  warm: function (...args) {
    log(levels.W, ...args);
  },
  error: function (...args) {
    log(levels.E, ...args);
  },
  setLogLevel: setLogLevel,
};

console = logger;

module.exports = {
  log: logger.log,
  info: logger.info,
  warn: logger.warn,
  error: logger.error,
  debug: logger.debug, 
  setLogLevel: setLogLevel,
  LEVEL: levels
};