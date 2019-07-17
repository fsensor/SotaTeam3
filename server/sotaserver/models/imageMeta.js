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
        collection: "versionInfo"
    }
));

const certificate= mongoose.model('certificate', new Schema(
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


module.exports = {
  version: version,
  certificate: certificate
};
