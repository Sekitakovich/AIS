function shipStatics(mmsi,mode,body) {
    var text = sprintf("Static: Vessel[%d] mode = %s name = %s", mmsi, mode, body['name']);
    console.log(text);
}

function shipDynamics(mmsi,body) {
    var text = sprintf("Dynamic: Vessel[%d] lat:lng = %f:%f", mmsi, body['lat'], body['lng']);
    console.log(text);
}

function dispatcher(news) {
    switch (news['type']) {
        case 'Vs':
            var mmsi = news['mmsi'];
            var data = news['data'];
            var mode = news['mode'];
            shipStatics(mmsi,mode,data);
            break;
        case 'Vd':
            var mmsi = news['mmsi'];
            var data = news['data'];
            shipDynamics(mmsi,data);
            break;
        case 'GPS':
            var data = news['data'];
            console.log(data);
            break;
        default:
            console.log(news);
            break;
    }
}
