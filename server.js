var fs = require('fs');

// function to encode file data to base64 encoded string
function base64_encode(file) {
    // read binary data
    var bitmap = fs.readFileSync(file);
    // convert binary data to base64 encoded string
    return Buffer.from(bitmap).toString('base64');
}

// function to create file from base64 encoded string
function base64_decode(base64str, file) {
    // create buffer object from base64 encoded string, it is important to tell the constructor that the string is base64 encoded
    var bitmap = new Buffer(base64str, 'base64');
    // write buffer to file
    fs.writeFileSync(file, bitmap);
    console.log('******** File created from base64 encoded string ********');
}

function handleResponse(resultPath){
    var count = 1 ;
    var jsonReturn = [];
    var files = fs.readdirSync(resultPath);
        //handling error
        //listing all files using forEach
    files.forEach(function (file) {
        //covert to base64
        var tmp = base64_encode(resultPath+file);   
        var key = "image"+count;
        count++;
        jsonReturn.push({[key]:tmp})
        fs.writeFileSync(__dirname+"//test.txt",tmp )
        //base64_decode(tmp, __dirname+"//"+file)
    });
    console.log(jsonReturn);
    return JSON.stringify(jsonReturn);
}
// convert image to base64 encoded string
//var base64str = base64_encode('kitten.jpg');
//console.log(base64str);
// convert base64 string back to image 
//base64_decode(base64str, 'copy.jpg');

var http = require('http');
const path = require('path')
var url = require('url')
const server = http.createServer().listen(3000);
server.on('request', (request, response) => {
    if(url.parse(request.url).pathname == "/callAPI"){
        if (request.method === "POST") {
            var body = "";  
            request.on("data", function (chunk) {
                body += chunk;
            });

            request.on("end", function(){
                body = JSON.parse(body) //JSON: {"UserID": "userID", "sesstionID": "sesstionID", "image1":"image1(base64)","image2":"...", ... , "image n": "..." }
                var value = Object.values(body); 
                var userID = value[0];
                var sesstionID = value[1];
                var imagePath = __dirname + "//images//"+ userID + "//" + sesstionID +"//";
                var resultPath = __dirname + "/images/" + userID + "/" + sesstionID+ "/results/";
                if (!fs.existsSync(imagePath)){
                    console.log("Images Directory not exists. Generating....")
                    fs.mkdirSync(imagePath,{ recursive: true });
                }
                if (!fs.existsSync(resultPath)){
                    console.log("Result Directory not exists. Generating....")
                    fs.mkdirSync(resultPath,{ recursive: true });
                }
                for(var i = 2; i < value.length; ++i){
                    //DECODE base64 to file and write image/{userID}/{sesstionID}/{i-1}.jpg
                    var imageName = imagePath + (i-1) + ".jpg";
                    base64_decode(value[i], imageName);
                }
                
                //---Execute python file
                var spawnSync = require("child_process").spawnSync;
                const pythonPath = path.join(__dirname, 'Acne_Detection_06092019_1000.py');
                var process = spawnSync('python',[pythonPath, userID, sesstionID]); //spawnSync(...,[arg1,arg2,arg3,...])
                if(process.status == 0) //OK
                {
                    //response result image to client
                    console.log(process.stdout.toString());
                    jsonReturn = handleResponse(resultPath)
                    response.writeHead(200, {"Content-Type": "application/json"});
                    response.end(jsonReturn);
                }
                else                    //ERROR
                {
                    console.log(process.stderr.toString())  //Log error from python
                    response.writeHead(200, {"Content-Type": "text/plain"});
                    response.end("There are some problems with server now. Please try again later!!!");
                }
            });
        }
        else if(request.method === "GET"){
            response.writeHead(200, {"Content-Type": "text/html"});
            response.write("random numbers that should come in the form of json");
            response.end();
        }
    }
});