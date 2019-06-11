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

/*
*   MMSI 先頭3文字は船籍(国名)
 */
const MMSInation = {
    201: 'Albania', 202: 'Andorra', 203: 'Austria', 204: 'Azores', 205: 'Belgium',
    206: 'Belarus', 207: 'Bulgaria', 208: 'Vatican City State',
    209: 'Cyprus', 210: 'Cyprus', 211: 'Germany',
    212: 'Cyprus', 213: 'Georgia', 214: 'Moldova', 215: 'Malta',
    216: 'Armenia', 218: 'Germany', 219: 'Denmark', 220: 'Denmark',
    224: 'Spain', 225: 'Spain', 226: 'France', 227: 'France', 228: 'France', 230: 'Finland', 231: 'Faroe Islands',
    232: 'United Kingdom of Great Britain and Northern Ireland',
    233: 'United Kingdom of Great Britain and Northern Ireland',
    234: 'United Kingdom of Great Britain and Northern Ireland',
    235: 'United Kingdom of Great Britain and Northern Ireland', 236: 'Gibraltar', 237: 'Greece',
    238: 'Croatia', 239: 'Greece', 240: 'Greece', 241: 'Greece', 242: 'Morocco',
    243: 'Hungary', 244: 'Netherlands', 245: 'Netherlands',
    246: 'Netherlands', 247: 'Italy', 248: 'Malta', 249: 'Malta', 250: 'Ireland', 251: 'Iceland',
    252: 'Liechtenstein', 253: 'Luxembourg', 254: 'Monaco', 255: 'Madeira',
    256: 'Malta', 257: 'Norway', 258: 'Norway', 259: 'Norway', 261: 'Poland', 262: 'Montenegro',
    263: 'Portugal', 264: 'Romania', 265: 'Sweden', 266: 'Sweden', 267: 'Slovak Republic',
    268: 'San Marino', 269: 'Switzerland (Confederation of)', 270: 'Czech Republic', 271: 'Turkey',
    272: 'Ukraine', 273: 'Russian Federation', 274: 'The Former Yugoslav Republic of Macedonia',
    275: 'Latvia', 276: 'Estonia', 277: 'Lithuania',
    278: 'Slovenia', 279: 'Serbia', 301: 'Anguilla', 303: 'Alaska (State of)',
    304: 'Antigua and Barbuda', 305: 'Antigua and Barbuda', 306: 'Netherlands Antilles', 307: 'Aruba',
    308: 'Bahamas', 309: 'Bahamas', 310: 'Bermuda',
    311: 'Bahamas', 312: 'Belize', 314: 'Barbados', 316: 'Canada', 319: 'Cayman Islands',
    321: 'Costa Rica', 323: 'Cuba', 325: 'Dominica', 327: 'Dominican Republic',
    329: 'Guadeloupe', 330: 'Grenada', 331: 'Greenland', 332: 'Guatemala',
    334: 'Honduras', 336: 'Haiti', 338: 'United States of America', 339: 'Jamaica',
    341: 'Saint Kitts and Nevis', 343: 'Saint Lucia', 345: 'Mexico',
    347: 'Martinique', 348: 'Montserrat', 350: 'Nicaragua', 351: 'Panama',
    352: 'Panama', 353: 'Panama', 354: 'Panama',
    358: 'Puerto Rico', 359: 'El Salvador',
    361: 'Saint Pierre and Miquelon', 362: 'Trinidad and Tobago',
    364: 'Turks and Caicos Islands', 366: 'United States of America', 367: 'United States of America',
    368: 'United States of America', 369: 'United States of America', 370: 'Panama',
    371: 'Panama', 372: 'Panama', 375: 'Saint Vincent and the Grenadines',
    376: 'Saint Vincent and the Grenadines', 377: 'Saint Vincent and the Grenadines',
    378: 'British Virgin Islands', 379: 'United States Virgin Islands', 401: 'Afghanistan',
    403: 'Saudi Arabia', 405: "Bangladesh", 408: 'Bahrain',
    410: 'Bhutan', 412: "China", 413: "China",
    416: 'Taiwan (Province of China)', 417: 'Sri Lanka',
    419: 'India', 422: 'Iran', 423: 'Azerbaijani Republic',
    425: 'Iraq', 428: 'Israel (State of)', 431: 'Japan', 432: 'Japan', 434: 'Turkmenistan',
    436: 'Kazakhstan', 437: 'Uzbekistan', 438: 'Jordan',
    440: 'Korea', 441: 'Korea',
    443: 'Palestine (In accordance with Resolution 99 Rev. Antalya, 2006)',
    445: "Democratic People's Republic of Korea", 447: 'Kuwait (State of)', 450: 'Lebanon', 451: 'Kyrgyz Republic',
    636: 'China',
    553: 'Papua New Guinea',
    374: 'Panama',
    477: 'Hong Kong',
    357: 'Panama',
    355: 'Panama',
    356: 'Panama',
    563: 'Singapore',
    564: 'Singapore',
    565: 'Singapore',
    566: 'Singapore',
    667: 'Sierra Leone',
    533: 'Malaysia',
    538: 'Marshall Islands',
    373: 'Mozambique',
};

/*
*   2点間の距離を得る関数
 */
function getDistance(lat1, lng1, lat2, lng2) {  // console.log(lat1,lng1,lat2,lng2)
    lat1 *= Math.PI / 180;
    lng1 *= Math.PI / 180;
    lat2 *= Math.PI / 180;
    lng2 *= Math.PI / 180;
    return 1000 * 6378.137 * Math.acos(Math.cos(lat1) * Math.cos(lat2) * Math.cos(lng2 - lng1) + Math.sin(lat1) * Math.sin(lat2));
}
