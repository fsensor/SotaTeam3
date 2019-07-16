var mongoose = require('mongoose');
var Schema = mongoose.Schema;

var imageMetaSchema = new Schema({
	version: String,
	path: String,
	type: String,
	date: { type: Date, default: Date.now  }
});

module.exports = mongoose.model('version', imageMetaSchema);
