'use strict';

const util = require('util');
const winston = require('winston');

require('winston-syslog').Syslog;

var syslogger = winston.createLogger({
    levels: winston.config.syslog.levels,
    transports: [
      new winston.transports.Syslog({
          protocol: 'udp4',
          port: '51451',
          facility: 'local3',
          localhost: 'SOTA',
          type: '5424',
          app_name: 'Server'
      })
    ]
});

var logger, 
  levels = {
    E: {
        value: 0,
        gt: level => { return this.value > level.value; },
        toSysLogLevel: () => { return "error"; }
    },
    W: {
        value: 1,
        gt: level => { return this.value > level.value; },
        toSysLogLevel: () => { return "warning"; }
    },
    D: {
        value: 2,
        gt: level => { return this.value > level.value; },
        toSysLogLevel: () => { return "debug"; }
    },
    I: {
        value: 3,
        gt: level => { return this.value > level.value; },
        toSysLogLevel: () => { return "info"; }
    },
  },
  currentLevel = levels.I,
  realConsole = console;


function doSyslog(level, message) {
  syslogger.log(level, message);
}

function log(level, ...args) {
  if (args.length === 0 || level.gt(currentLevel)) {
    return;
  }

  let message = util.format(...args);

  realConsole.log(Date.now() + ': ' + message.substring(0, message.lastIndexOf('SIGN [')));
  doSyslog(level.toSysLogLevel(), message);
}

function getCurrentLogLevel() {
  return currentLevel;
}

function setLogLevel(level) {
  if (typeof level !== 'number') {
    return;
  }
  currentLevel = level;
}

function setConsole(newconsole) {
  if (realConsole !== newconsole && newconsole !== logger) {
    realConsole = newConsole;  
  }
}


logger = {
  log: function (level, ...args) {
    log(level, ...args);
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
  getCurrentLogLevel: getCurrentLogLevel,
  setLogLevel: setLogLevel,
  setConsole: setConsole,
  LEVEL: levels
};

