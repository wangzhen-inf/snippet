// generate test data for multi-picklist 
var fs = require('fs');

console.log(process.argv);

fs.readFile('option.set', { encoding: "utf8" },function( err, data){
    if(err) throw err;
    console.log(data);
});
