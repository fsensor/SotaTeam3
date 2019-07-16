const MongoClient = require('mongodb').MongoClient;
const fs = require('fs');

var port = null;
var host = null;

var dbName = null;
var imageinfo = null;
var collection = null;

var forceInit = false;
var removeDB = false;

let cmdLineOptions = process.argv.slice(2);

function getOption(option, prefix) {
  let name = option.replace(prefix, '', 1);
  let value = null;
  if (name !== '') {
    value = name;
  }
  return value;
}

var optionprocessor = [
  {
      prefix: 'dbname=',
      set: (option) => dbName = getOptions(option, this->prefix)
  },
  {
      prefix: 'imageinfo=',
      set: (option) => imageinfo = getOptions(option, this->prefix)
  },
  {
      prefix: 'host=',
      set: (option) => host = getOptions(option, this->prefix)
  },
  {
      prefix: 'port=',
      set: (option) => port = getOptions(option, this->prefix)
  }
];

for (let option of cmdLineOptions) {
  console.log('process option ' + option)
  for (let opt_processor of optionprocessor) {
    if (option.startsWith(opt_processor.prefix) {
      opt_processor.set(option);
    } 
  }
}

if (port === null || host === null || dbName === null || imageinfo === null) {
  console.log('host, port, db name, and a file for image information must be given');
  return;
}

MongoClient.connect(
  'mongodb://' + host + ':' + port + '/admin',
  { useNewUrlParser: true },
  async (err, client) => {
    if (err) {
      console.error(
        'DB connection error to [%s:%d] => %s',
        host, 
        port,
        str(err)
      );
      return;
    }
    let database = client.db();
    let dbList = await database.command({ listDatabases : 1 });
    
    console.log('Current List of DB => ');
    console.log(dbList);
     
    
    console.log('(Create and) Add data to %s database', dbName);
    let targetDB = client.db(dbName);
    let collectionList = await targetDB.command(
        { listCollections: 1, nameOnly: true }
    );

    let imageinfodatas;

    try { 
      imageinfodatas = JSON.parse(fs.readFileSync(imageinfo));
    } catch () {
      console.log("Exception while reading and parsing %s file", imageinfo);
      return;
    }
    
    for (let [collection, data] of imageinfodatas) {
      let existed = false;
      for (let existed of collectionList) {
        if (existed.name === collection) {
          existed = true;
        }
      }
      if (!existed) {
        console.log('Creating collection ' + collection);
        await targetDB.createCollection(collection);
      }
      await targetDB
          .collection(collection)
          .insertMany(data);
    }

    console.log('All Done');

    dbList = await database.command({ listDatabases : 1 });
    
    console.log('Updated List of DB => ');
    console.log(dbList);

    client.close();
  }
);
