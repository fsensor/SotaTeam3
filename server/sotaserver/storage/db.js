'use strict';

var fs = require("fs");
var asynccaller = require('../common/asynccaller.js');

const ERROR_CODES = require('../common/errorcodes.js');

function getCert() {
	return fs.readFileSync("test/cert/cert.pem");
}

function getKey() {
	return fs.readFileSync("test/cert/key.pem");
}

function getVersion(onResult) {
	if (typeof onResult !== 'function') {
		return;
	}
	// TODO: Read from real db
	asynccaller.call(
			onResult,
			ERROR_CODES.SUCCESS,
			'{ "version_info": [{ "version_type": "latest", "version": "2", "image_name": "test.txt", "image_type": "text", "priorty": "urgent" }] }'
	);	
}

function getLatestImagePath(onResult) {
	if (typeof onResult !== 'function') {
		return;
	}
	asynccaller.call(
		onResult,
		ERROR_CODES.SUCCESS,
		'test/image/sample_data_file_server'
	);
}

module.exports = {
	getCert: getCert,
	getKey: getKey,
	getVersion: getVersion,
	getLatestImagePath: getLatestImagePath
}
