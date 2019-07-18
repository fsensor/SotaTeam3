var mongoose = require('mongoose');
var Schema = mongoose.Schema;

const version = mongoose.model('version', new Schema(
    {
        version: String,
        path: String,
        type: String,
        date: String
    },
    {
        _id: false,
        collection: "imageMeta"
    }
));

const certificate = mongoose.model('certificate', new Schema(
    {
        cert: String,
        key: String,
        cacert: String
    },
    {
        _id: false,
        collection: "certificate"
    }
));

const fingerprint = mongoose.model('fingerprint', new Schema(
    {
        value: String,
    },
    {
        _id: false,
        collection: "fingerprint"
    }
));

module.exports = {
  version: version,
  certificate: certificate,
  fingerprint: fingerprint
};
