'use strict';

const resolvedPromise = new Promise(resolve => resolve());

async function callAsync(functionToCall, ...args) {
  await resolvedPromise;
  if (typeof functionToCall === 'function') {
    functionToCall.apply(this, args);
  }
  return;
}

module.exports = { call: callAsync }
