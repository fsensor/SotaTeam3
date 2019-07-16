'use strict';

var fs = require("fs");
var asynccaller = require('../common/asynccaller.js');

var ImageMeta = require('../models/imageMeta');

// CONNECT TO MONGODB SERVER
var mongoose = require('mongoose');
var db = mongoose.connection;
db.on('error', console.error);
db.once('open', function(){
    // CONNECTED TO MONGODB SERVER
    console.log("Connected to mongod server");
});
mongoose.connect('mongodb://localhost/mongodb_imageMeta', { useNewUrlParser: true });

const ERROR_CODES = require('../common/errorcodes.js');

function getCert() {
	return fs.readFileSync("test/cert/cert.pem");
}

function getKey() {
	return fs.readFileSync("test/cert/key.pem");
}

function getCACert() {
	return fs.readFileSync("test/cert/CACert.pem");
}

function getVersion(onResult) {
	if (typeof onResult !== 'function') {
		return;
	}
	// TODO: Read from real db
	ImageMeta.find(function(err, images) {
		if (err) {
			asynccaller.call(
				onResult,
				ERR_INTERNAL_ERROR,
				'error'
			);
		} else {		
			asynccaller.call(
				onResult,
				ERROR_CODES.SUCCESS,
				//'{ "version_info": [{ "version_type": "latest", "version": "2", "image_name": "test.txt", "image_type": "text", "priorty": "urgent" }] }'
				images
			);
		}
	});
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
	getCACert : getCACert,
	getKey: getKey,
	getVersion: getVersion,
	getLatestImagePath: getLatestImagePath
}
