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
      set: (option, prefix) => dbName = getOption(option, prefix)
  },
  {
      prefix: 'imageinfo=',
      set: (option, prefix) => imageinfo = getOption(option, prefix)
  },
  {
      prefix: 'host=',
      set: (option, prefix) => host = getOption(option, prefix)
  },
  {
      prefix: 'port=',
      set: (option, prefix) => port = getOption(option, prefix)
  }
];

for (let option of cmdLineOptions) {
  for (let opt_processor of optionprocessor) {
    if (option.startsWith(opt_processor.prefix)) {
      opt_processor.set(option, opt_processor.prefix);
    } 
  }
}

if (typeof port !== 'string' || typeof host !== 'string' ||
    typeof dbName !== 'string' || typeof imageinfo !== 'string') {
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
        { listCollections: 1 }
    );
    let imageinfodatas;
    

    try { 
      imageinfodatas = JSON.parse(fs.readFileSync(imageinfo));
    } catch (error) {
      console.log("Exception %s while reading and parsing %s file", error, imageinfo);
      client.close();
      return;
    }
     
    for (let [collection, data] of Object.entries(imageinfodatas)) {
      let existed = false;

      console.log('Current collection => ');
      for (let existedcollection of collectionList.cursor.firstBatch) {
        console.log(existedcollection);
        await targetDB
            .collection(existedcollection.name)
            .find()
            .forEach(item => console.log(item));
        if (existedcollection.name === collection) {
          existed = true;
          break;
        }
      }
    

      if (!existed) {
        console.log('Creating collection ' + collection);
        await targetDB.createCollection(collection);
      }
      
      for (let item of data) {
        await new Promise(resolve => targetDB.collection(collection)
            .find({ version: item.version})
            .count(
                true,
                {limit:1}, 
                (error, count) => {
                  if (error) {
                    resolve();
                    return;
                  }
                  
                  if (count == 0) {
                    console.log('insert %s!', item);
                    new Promise(insertResolve => {
                      targetDB
                        .collection(collection)
                        .insertOne(item);
                      insertResolve();
                      resolve();
                    });
                  } else {
                    console.log('Item to isert');
                    console.log('%s alredy exist!', item);
                    resolve();
                  }
                }
            )
        );
      }
    }

    console.log('All Done');

    dbList = await database.command({ listDatabases : 1 });
    
    console.log('Updated List of DB => ');
    console.log(dbList);

    collectionList = await targetDB.command(
        { listCollections: 1 }
    )

    console.log('Updated collection => ');
    for (let existedcollection of collectionList.cursor.firstBatch) {
      console.log(existedcollection);
      await targetDB
          .collection(existedcollection.name)
          .find()
          .forEach(item => console.log(item));
    }

    client.close();
  }
);
