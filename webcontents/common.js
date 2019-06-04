// var GPGGA = function () {
//     this.quality = 0;
//     this.ss = 0;
// };
//
// var infoGGA = new GPGGA();
//
//
function shipStatics(mmsi, type, body) {
    var text = sprintf("Ship %d Type: %d name = %s", mmsi, type, body['shipname']);
    console.log(text);
}

function shipDynamics(mmsi, type, body) {
    var text = sprintf("Ship %d Type: %d lat:lng = %f:%f", mmsi, type, body['maplat'], body['maplng']);
    console.log(text);
}

function dispatcher(news) {
    var data = news['data'];
    switch (news['mode']) {
        case 'AIS':
            var header = data['header'];
            var body = data['body'];
            switch (header['type']) {
                // case 1:
                // case 2:
                // case 3:
                // case 18:
                //     shipDynamics(header['mmsi'], header['type'], body);
                //     break;
                case 5:
                case 24:
                    shipStatics(header['mmsi'], header['type'], body);
                    break;
                case 19:
                    shipStatics(header['mmsi'], header['type'], body);
                    // shipDynamics(header['mmsi'], header['type'], body);
                    break;
                case 6:
                case 8:
                    console.log(data);
                    break;
                default:
                    break;
            }
            break;
        case 'GPRMC':
            var lat = data['maplat'];
            var lng = data['maplng'];
            // console.log(lat, lng);
            break;
        case 'GPGGA':
            // console.log(data);
            var quality = data['quality'];
            var ss = data['ss'];
            // if (quality != infoGGA.quality || ss != infoGGA.ss) {
            //     infoGGA.quality = quality;
            //     infoGGA.ss = ss;
            //     console.log(infoGGA);
            // }
            console.log(data);
            break;
        default:
            console.log(data);
            break;
    }
}
