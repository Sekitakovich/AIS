let stage = null;

/*
*   AtoN - 受信したものは出しっぱなし
 */
class AtoN {

    constructor(name, lat, lon) {
        this.marker = null;
        this.update(name, lat, lon);
    }

    update(name, lat, lon) {
        this.name = name;
        this.lat = lat;
        this.lon = lon;
        this.at = new Date();
    }

}

/*
*   他船
*   当初は「静的情報に動的情報を紐付ける」としたが、最新の仕様では船舶の名称やIMO、
*   コールサインといったデータがあまり意味を持たないので動的情報優先とした。
 */
class Enemy {

    constructor(lat, lon, sog, cog, status, nation) {
        this.update(lat, lon, sog, cog, status);
        this.marker = null;
        this.inRed = false; // ガードゾーン内にあればtrue
        this.haveStatic = false;
        this.nation = nation;
    }

    update(lat, lon, sog, cog, status) {
        this.lat = lat;
        this.lon = lon;
        this.sog = sog;
        this.cog = cog;
        this.status = status;
        this.at = new Date();
    }

    getRedCondition() {
        return this.inRed;
    }

    setRedCondition(condition) {
        this.inRed = condition;
    }
}

/*
*   メインとなるクラス
 */
class Stage {

    constructor(mapStage) {

        this.cacheTheShip = true;
        this.shipInfoTimeout = (60 * 60 * 24 * 1);
        this.dynamicTimeout = (60 * 3 * 1.5);

        jQuery('#reset').on('click', function (e) {
            if (confirm('Reset all statistics OK?')) {
                localStorage.removeItem('shipinfo');
                window.location.reload();
            }
        });

        this.AtoN = {}; // key = mmsi
        this.atonToolTip = false;
        this.atonButton = jQuery('#atonButton');
        this.atonButton.on('click', function (e) {
            if (stage.atonToolTip) {
                for (let c in stage.AtoN) {
                    stage.AtoN[c]['marker'].closeTooltip();
                }
                stage.atonToolTip = false;
            } else {
                for (let c in stage.AtoN) {
                    stage.AtoN[c]['marker'].openTooltip();
                }
                stage.atonToolTip = true;
            }
        });

        if ("latlng" in localStorage) {
            this.latlng = JSON.parse(localStorage.getItem("latlng")); //console.log(baseLatLng);
        } else {
            this.latlng = {'lat': 0.0, 'lon': 0.0};
        }
        this.latText = jQuery('#Lat');
        this.lngText = jQuery('#Lng');
        this.ewns = {'lat': 'N', 'lon': 'E'};

        if (this.cacheTheShip && "shipinfo" in localStorage) {
            let shipinfo = JSON.parse(localStorage.getItem("shipinfo"));
            for (let s in shipinfo) {
                shipinfo[s]['at'] = new Date(shipinfo[s]['at']);
            }
            this.shipinfo = shipinfo;
            console.log('restored shipinfo');
            // console.log(shipinfo);
        } else {
            localStorage.removeItem("shipinfo");
            this.shipinfo = {};  // enemies static : key = mmsi
        }

        setInterval(function (e) {
            stage.manageStatistics();
        }, 1000 * 60);
        this.manageStatistics();

        this.eSymbol = {}; // enemies dynamic : key = mmsi
        // this.shipToolTip = false;
        // this.shipButton = jQuery('#shipButton');
        // this.shipButton.on('click',function(e){
        //     if(stage.shipToolTip){
        //         for(let c in stage.eSymbol){
        //             if(stage.eSymbol[c]['marker']){
        //                 stage.eSymbol[c]['marker'].closeTooltip();
        //             }
        //         }
        //         stage.shipToolTip = false;
        //     }
        //     else{
        //         for(let c in stage.eSymbol){
        //             if(stage.eSymbol[c]['marker']){
        //                 // console.log(stage.eSymbol[c]['marker'])
        //                 stage.eSymbol[c]['marker'].openTooltip();
        //             }
        //         }
        //         stage.shipToolTip = true;
        //     }
        // });

        this.autoScroll = true;
        this.autoRange = true;

        this.soundEnable = false;
        this.alarmSound = new Audio('webcontents/sounds/tomvy.mp3');
        this.inAlarm = false; // 警告音鳴動中は真
        this.soundOnOff = jQuery('#soundOnOff');
        this.soundBox = jQuery('#soundBox').val(this.soundEnable ? 'On' : 'Off');
        this.soundOnOff.on('click', function (e) {
            if (stage.soundEnable) {
                stage.soundBox.val('Off');
                stage.soundEnable = false;
            } else {
                stage.soundBox.val('On');
                stage.soundEnable = true;
                stage.alarmSound.play(); // notice! for iOS
            }
            console.log('Sound is ' + stage.soundEnable);
        });

        this.levelMaster = [
            {'radius': 0.125, 'zoom': 16, 'sog': 5},
            {'radius': 0.250, 'zoom': 15, 'sog': 10},
            {'radius': 0.5, 'zoom': 14, 'sog': 15},
            {'radius': 1, 'zoom': 13, 'sog': 20},
            {'radius': 2, 'zoom': 12, 'sog': 25},
            {'radius': 4, 'zoom': 11, 'sog': 40},
            {'radius': 8, 'zoom': 10, 'sog': 10000},
        ];
        this.zoneMax = this.levelMaster.length - 1;
        this.currentZone = 0;

        this.redZone = this.levelMaster[this.currentZone]['radius'] * 1852;
        this.greenZone = this.redZone * 2;

        this.ZN = jQuery('#ZN');
        this.ZN.on('click', function (e) {
            if (stage.currentZone) {
                console.log('Narrow');
                stage.currentZone -= 1;
                stage.changeTheLevel();
            }
        });
        this.ZW = jQuery('#ZW');
        this.ZW.on('click', function (e) {
            if (stage.currentZone < stage.zoneMax) {
                console.log('Wide');
                stage.currentZone += 1;
                stage.changeTheLevel();
            }
        });
        this.autoRangeButton = jQuery('#autoRange');
        this.autoRangeBox = jQuery('#rangeBox').val(this.autoRange ? 'On' : 'Off');
        if (this.autoRange == true) {
            this.ZN.prop('disabled', true);
            this.ZW.prop('disabled', true);
        }
        this.autoRangeButton.on('click', function (e) {
            // console.log(e)
            if (stage.autoRange == true) {
                stage.autoRange = false;
                stage.autoRangeBox.val('Off');
                stage.ZN.prop('disabled', false);
                stage.ZW.prop('disabled', false);
                stage.Map.scrollWheelZoom.enable();
            } else {
                stage.autoRange = true;
                stage.autoRangeBox.val('On');
                stage.ZN.prop('disabled', true);
                stage.ZW.prop('disabled', true);

                stage.Map.panTo(stage.latlng);
                stage.Map.setZoom(stage.levelMaster[stage.currentZone]['zoom']);
                stage.autoScroll = true;
                stage.autoScrollBox.val('AUTO');
                stage.Map.scrollWheelZoom.disable();

            }
            // const zoom = stage.levelMaster[stage.currentZone]['zoom'];
            // console.log('Zoom = ',zoom);
        });
        this.rangeText = jQuery('#rangeText'); //console.log('RT = ',this.rangeText);

        this.autoscrollButton = jQuery('#autoscroll');
        this.autoScrollBox = jQuery('#scrollBox').val(this.autoScroll ? 'AUTO' : 'MANUAL');
        this.autoscrollButton.on('click', function (e) {
            // console.log(e)
            if (stage.autoScroll == true) {
                stage.autoScroll = false;
                stage.autoScrollBox.val('MANUAL');
            } else {
                stage.autoScroll = true;
                stage.autoScrollBox.val('AUTO');
                stage.Map.panTo(stage.latlng);
            }
        });

        this.Map = L.map(mapStage, {
            zoomControl: false,
        }).setView(this.latlng, 16);

        this.Map.scrollWheelZoom.disable();

        L.tileLayer("webcontents/tiles/{z}/{x}/{y}.png", {
            minZoom: 10,
            maxZoom: 16,
            // scrollWheelZoom: false, // Why?
            id: 'map',
        }).addTo(this.Map);
        L.control.scale({
            'metric': false,
        }).addTo(this.Map);
        console.log('Map', this.Map);

        let clock = new L.Control.Clock();
        clock.addTo(this.Map);
        leaflet_control_clock();


        this.Map.on('zoomend', function (e) {
            console.log('Zoomlevel = ' + this.getZoom()); // Notice!
        });

        this.Map.on('load', function (e) {
            console.log('Map was loaded');
        });

        this.Map.on('drag', function (e) {
            // console.log('drag');
            if (stage.autoScroll == true) {
                stage.autoScroll = false;
                stage.autoScrollBox.val('MANUAL');
            }
        });

        this.redCircle = L.circle(this.latlng, {
            radius: this.redZone,
            color: 'red',
            fillColor: '#FFFFFF',
            fillOpacity: 0.3,
        }).addTo(this.Map);
        this.greenCircle = L.circle(this.latlng, {
            radius: this.greenZone,
            color: 'green',
            fillColor: '#000000',
            fillOpacity: 0.1,
        }).addTo(this.Map);

        this.myShip = L.marker(this.latlng, {
            rotationAngle: 0,
            rotationOrigin: 'center center',
            icon: L.icon({
                iconUrl: 'webcontents/imgs/tomvyS.png', // 48x48
                // iconUrl: 'imgs/tb2.png', // 48x48
                iconAnchor: [24, 24],
                title: 'Tomvy',
                riseOnHover: true,
                zIndex: 100,
            }),
        }).addTo(this.Map);
        L.DomUtil.addClass(this.myShip._icon, 'tomvy');

        this.icons = {
            'kaniS': this.createIcon('kaniS', 24),
            'kani': this.createIcon('kani', 32),
            'kame': this.createIcon('kameS', 24),
            'enterX': this.createIcon('enterX', 24),
            'anchor': this.createIcon('anchor', 24),
            'fish': this.createIcon('fish', 24),
            'question-mark': this.createIcon('question-mark', 24),
            'ant': this.createIcon('ant', 24),
            'rocket': this.createIcon('rocket', 32),
            'warn': this.createIcon('warn', 24),
            'drum': this.createIcon('drum', 24),
            'walker': this.createIcon('walker', 24),
            'notEnter': this.createIcon('notEnter', 16),
            'shuri-ken': this.createIcon('shuri-ken', 16),
            'ufo': this.createIcon('ufo', 24),
            'daruma': this.createIcon('daruma', 16),
            'man': this.createIcon('man', 24),
            'heart': this.createIcon('heart', 24),
            'oil': this.createIcon('oil', 24),
            'human': this.createIcon('human', 24),
        }; // console.log(this.icons);

        this.sogMeter = new JustGage({
            id: "sogMeter",
            value: 0,
            min: 0,
            max: 60,
            symbol: 'kn',
            title: "Speed",
            label: "Knot",
            pointer: true,
            levelColors: ['Lightblue'],
            // customSectors: [
            //     {'lo': 0,'hi': 15, 'color': 'Green'},
            //     {'lo': 15.1,'hi': 25, 'color': 'Yellow'},
            //     {'lo': 25.1,'hi': 10000, 'color': 'Red'},
            // ],
            levelColorsGradient: false,
            pointerOptions: {
                toplength: -15,
                bottomlength: 10,
                bottomwidth: 12,
                color: 'Red',
                stroke: '#FFFFFF',
                stroke_width: 3,
                stroke_linecap: 'round'
            },
            gaugeWidthScale: 0.6,
            counter: true,
        });


    };

    manageStatistics() {
        const now = new Date().getTime();
        for (let s in this.shipinfo) { // console.log(this.shipinfo[s])
            const secs = (now - this.shipinfo[s]['at'].getTime()) / 1000;
            if (secs > this.shipInfoTimeout) {
                delete (this.shipinfo[s]);
                console.log('Delete statistics ', s);
            }
        }
    }

    changeTheLevel() {
        const radius = this.levelMaster[this.currentZone]['radius'];
        this.redZone = radius * 1852 * 1;
        this.greenZone = this.redZone * 2;
        this.Map.setZoom(this.levelMaster[this.currentZone]['zoom']);
        this.redrawCircle();
        this.rangeText.val(radius);
    }

    createIcon(name, wh) {// console.log(name);
        let img = new Image(); // console.log(img);
        const url = 'webcontents/imgs/' + name + '.png';
        img.src = url;
        const icon = L.icon({
            iconUrl: url,
            iconAnchor: [wh / 2, wh / 2],
            name: name,
        });
        return icon;
    }

    redrawCircle() {
        console.log('currentZone = ', this.currentZone);
        // console.log(this.redZone,this.greenZone);
        this.redCircle.setRadius(this.redZone);
        this.greenCircle.setRadius(this.greenZone);
        for (var mmsi in this.eSymbol) {
            this.manageMarker(mmsi);
        }
    }

    // checkDistance(point) {
    //     let lat1 = this.latlng['lat'];
    //     let lon1 = this.latlng['lon'];
    //     let lat2 = point['lat'];
    //     let lon2 = point['lng'];
    //
    //     const ooo = getDistance(lat1, lon1, lat2, lon2);
    //     console.log(ooo);
    // }

    // 自船とmmsiで示される他船との距離をメートルで得る関数
    distance(mmsi) {
        const meter = getDistance(
            this.latlng['lat'],
            this.latlng['lon'],
            this.eSymbol[mmsi]['lat'],
            this.eSymbol[mmsi]['lon']);
        // console.log(meter);
        return meter;
    }

    /*
    *   他船アイコンの制御
     */
    manageMarker(mmsi, flag) {

        const owner = this.eSymbol[mmsi]; //console.log(owner);
        const meter = this.distance(mmsi); // console.log(meter);
        const secs = (new Date().getTime() - owner['at'].getTime()) / 1000;

        if (secs > this.dynamicTimeout) { // タイムアウト＝登録抹消
            if (owner['marker']) {
                this.Map.removeLayer(owner['marker']);
            }
            delete (this.eSymbol[mmsi]);
            console.log('--- del ', mmsi);
        } else if (meter < this.greenZone || true) {
            const latlng = {'lat': owner['lat'], 'lon': owner['lon']};
            let opacity = 0.5;
            let name = '';
            let rotate = false;
            let inRed = false;
            let cog = 0;

            // if (meter < this.redZone) {
            // if(flag == 'R' || flag == 'X'){ console.log(mmsi);
            //     inRed = true;
            // }
            // else{
            //     opacity = 0.5;
            // }

            switch (flag) {
                case 'F':
                    break;
                case 'G':
                    opacity = 0.5;
                    break;
                case 'R':
                    opacity = 1.0;
                    break;
                case 'X':
                    opacity = 1.0;
                    inRed = true;
                    break;
                default:
                    break;
            }
            if (false) {
                ;
            }
            // if (secs > (60 * 3)) {
            //     name = 'question-mark';
            //     if (owner['marker']) {
            //         this.Map.removeLayer(owner['marker']);
            //         owner['marker'] = null;
            //         // console.log('??? ', mmsi);
            //     }
            // }
            else {
                switch (owner['status']) {
                    case 1: // 停泊中
                    case 4: // 曳航され中
                        // name = 'enterX';
                        name = 'notEnter';
                        break;
                    case 5: // 係留中
                        name = 'anchor';
                        break;
                    case 7: // 漁労中
                        name = 'fish';
                        break;
                    default:
                        if (owner['haveStatic']) { //console.log(this.shipinfo[mmsi]['item']['shiptype']);
                            // name = 'kani';
                            // name = 'ant';
                            switch (parseInt(this.shipinfo[mmsi]['item']['type']) / 10) {
                                case 4:
                                    name = 'warn';
                                    break;
                                case 5:
                                    name = 'fish';
                                    break;
                                case 6:
                                    name = 'human';
                                    break;
                                case 7:
                                    name = 'kame';
                                    break;
                                case 8:
                                    name = 'oil';
                                    break;
                                default:
                                    name = 'kaniS';
                                    break;
                            }
                        } else {
                            name = 'daruma';
                        }
                        rotate = true;
                        cog = owner['cog'];
                        break;
                }
            }

            if (owner['marker'] == null) { //console.log(name);
                const marker = L.marker(latlng, {
                    rotationOrigin: 'center center',
                    icon: this.icons[name],
                    name: mmsi,
                    singleClickTimeout: 250,
                }).addTo(this.Map); //console.log(marker);

                let shipName = '';
                let callSign = '';
                if (mmsi in this.shipinfo) {
                    shipName = this.shipinfo[mmsi]['item']['shipname'];
                    callSign = this.shipinfo[mmsi]['item']['callsign'];
                }
                const flag = '<img src="webcontents/nationFlags/' + owner['nation'] + '.png">';
                const text = flag + ' ' + mmsi.toString() + ' (' + owner['nation'] + ')';
                let html = [];
                html.push(flag);
                if (shipName) {
                    html.push(shipName);
                }
                if (callSign) {
                    html.push(callSign);
                }
                marker.bindTooltip(text);
                marker.bindPopup(html.join('<br>'));

                marker.on('singleclick', function (e) { // for debug
                    const name = e.target.options.name;
                    console.log(name, stage.eSymbol[name]);
                    if (name in stage.shipinfo) {
                        console.log(stage.shipinfo[name]);
                    }
                });

                owner['marker'] = marker;

                // console.log('1st: ',owner['marker']._icon)
            }

            owner['marker'].setRotationAngle(cog);
            owner['marker'].setLatLng(latlng);
            owner['marker'].setOpacity(opacity);
            if (inRed == true && owner.getRedCondition() == false) {
                if (rotate) {
                    L.DomUtil.addClass(owner['marker']._icon, 'blinking');
                    // owner['marker'].openPopup();
                    // owner['marker'].openTooltip();
                    // console.log('+++: ',owner['marker']._icon)
                }
                owner.setRedCondition(true);
            } else if (inRed == false && owner.getRedCondition() == true) {
                if (rotate) {
                    L.DomUtil.removeClass(owner['marker']._icon, 'blinking');
                    // owner['marker'].closePopup();
                    // owner['marker'].closeTooltip();
                }
                owner.setRedCondition(false);
            }
        } else if (owner['marker']) {
            this.Map.removeLayer(owner['marker']);
            owner['marker'] = null;
            console.log('--- out ', mmsi);
        }

        // if(this.autoRange) {
        //     this.Map.setZoom(this.levelMaster[this.currentZone]['zoom']);
        // }

    }

    manageSound() {
        if (this.soundEnable) {
            let reds = false;
            for (let e in this.eSymbol) {
                if (this.eSymbol[e]['inRed']) {
                    reds = true;
                    break;
                }
            }
            if (reds) {
                if (this.inAlarm) {
                    ;
                } else {
                    this.alarmSound.play();
                    this.inAlarm = true;
                }
            } else {
                this.inAlarm = false;
            }
        }
    }

    onAtoN(mmsi, item) { //console.log(item);
        const lat = item['plus']['lat'];
        const lon = item['plus']['lon'];
        const latlng = {'lat': lat, 'lon': lon};
        if (mmsi in this.AtoN == false) {
            this.AtoN[mmsi] = new AtoN(item['name'], lat, lon);
            this.AtoN[mmsi]['marker'] = L.marker(latlng, {
                icon: L.icon.pulse({iconSize: [8, 8], color: 'Blue'}),
                zIndex: 25,
            }).addTo(this.Map);

            this.AtoN[mmsi]['marker'].bindTooltip(item['name']);
            console.log(this.AtoN);
        } else {
            this.AtoN[mmsi].update(item[name], lat, lon)
        }
    }

    onVDO(item) { // console.log(item);

        const sog = item['sog'];
        this.sogMeter.refresh(sog);
        if (this.autoRange) {
            let index = 0;
            for (let c of this.levelMaster) {
                if (sog <= c['sog']) {
                    break;
                }
                index++;
            }
            if (index != this.currentZone) {
                console.log('sog =', sog, ' range ', index);
                this.currentZone = index;
                this.changeTheLevel();
            }
        }

        this.latlng['lat'] = item['lat'];
        this.latlng['lon'] = item['lon'];

        this.ewns['lat'] = item['ns'];
        this.ewns['lon'] = item['ew'];

        this.latText.val(item['ns'] + ' ' + item['lat'].toFixed(3));
        this.lngText.val(item['ew'] + ' ' + item['lon'].toFixed(3));

        if (this.autoScroll) {
            this.Map.panTo(this.latlng);
        }
        this.myShip.setLatLng(this.latlng);
        this.myShip.setRotationAngle(item['cog']);
        this.redCircle.setLatLng(this.latlng);
        this.greenCircle.setLatLng(this.latlng);
        for (var mmsi in this.eSymbol) {
            this.manageMarker(mmsi);
        }

        this.manageSound();
        localStorage.setItem("latlng", JSON.stringify(this.latlng));
    }

    onVDM(info) { // console.log(info);
        const mmsi = info['mmsi'];
        switch (info['type']) {
            case 1:
            case 2:
            case 3:
            case 18:
                const item = info['item'];
                if ((mmsi in this.eSymbol) == false) {
                    const code3 = parseInt(mmsi.toString().substr(0, 3));
                    let nation = '???';
                    if (code3 in MMSInation) {
                        nation = MMSInation[code3];
                    }
                    this.eSymbol[mmsi] = new Enemy(item['plus']['lat'], item['plus']['lon'], item['speed'], item['course'], item['status'], nation);
                } else {
                    this.eSymbol[mmsi].update(item['plus']['lat'], item['plus']['lon'], item['speed'], item['course'], item['status']);
                }
                if (mmsi in this.shipinfo) { // 先に動的情報を受信していた場合
                    this.eSymbol[mmsi].haveStatic = true;
                }
                this.manageMarker(mmsi);
                this.manageSound();
                break;
            case 5:
            case 24:
                // console.log('shiptype = ',info['item']['shiptype']);
                if ((mmsi in this.shipinfo) == false) {
                    const now = new Date(); // console.log(now);
                    this.shipinfo[mmsi] = {'at': now, 'item': info['item']};

                    const code3 = parseInt(mmsi.toString().substr(0, 3));
                    let nation = '???';
                    if (code3 in MMSInation) {
                        nation = MMSInation[code3];
                    } // console.log('Type',info['type'], code3, nation);

                    if (mmsi in this.eSymbol) { // 先に動的情報を受信していた場合
                        this.eSymbol[mmsi]['haveStatic'] = true;
                        if (this.eSymbol[mmsi]['marker']) {
                            this.Map.removeLayer(this.eSymbol[mmsi]['marker']);
                            this.eSymbol[mmsi]['marker'] = null;
                        }
                        if (this.eSymbol[mmsi].getRedCondition() == true) {
                            this.eSymbol[mmsi].setRedCondition(false);
                        }
                        this.manageMarker(mmsi);
                        console.log('Catch static ', mmsi);
                    }
                    if (this.cacheTheShip) {
                        localStorage.setItem("shipinfo", JSON.stringify(this.shipinfo)); // Notice!
                    }
                }
                break;
            case 21: // AtoN
//            console.log(info);
                this.onAtoN(mmsi, info['item']);
                break;
            default:
                break;
        }
    }

    onGPS(data) {
        const sog = data['sog'];
        this.sogMeter.refresh(sog);

        if (this.autoRange) {
            let index = 0;
            for (let c of this.levelMaster) {
                if (sog <= c['sog']) {
                    break;
                }
                index++;
            }
            if (index != this.currentZone) {
                console.log('sog =', sog, ' range ', index);
                this.currentZone = index;
                this.changeTheLevel();
            }
        }

        this.latlng['lat'] = data['lat'];
        this.latlng['lon'] = data['lng'];

        this.ewns['lat'] = data['ns'];
        this.ewns['lon'] = data['ew'];

        this.latText.val(data['ns'] + ' ' + data['lat'].toFixed(3));
        this.lngText.val(data['ew'] + ' ' + data['lng'].toFixed(3));

        if (this.autoScroll) {
            this.Map.panTo(this.latlng);
        }
        this.myShip.setLatLng(this.latlng);
        this.myShip.setRotationAngle(data['cog']);
        this.redCircle.setLatLng(this.latlng);
        this.greenCircle.setLatLng(this.latlng);
        for (var mmsi in this.eSymbol) {
            this.manageMarker(mmsi);
        }

        this.manageSound();
        localStorage.setItem("latlng", JSON.stringify(this.latlng));

    }

    onAISS(mmsi, data, mode) {
        console.log('S', mmsi, mode, data);
        if ((mmsi in this.shipinfo) == false) {
            const now = new Date(); // console.log(now);
            this.shipinfo[mmsi] = {'at': now, 'item': data};

            const code3 = parseInt(mmsi.toString().substr(0, 3));
            let nation = '???';
            if (code3 in MMSInation) {
                nation = MMSInation[code3];
            } // console.log('Type',info['type'], code3, nation);

            if (mmsi in this.eSymbol) { // 先に動的情報を受信していた場合
                this.eSymbol[mmsi]['haveStatic'] = true;
                if (this.eSymbol[mmsi]['marker']) {
                    this.Map.removeLayer(this.eSymbol[mmsi]['marker']);
                    this.eSymbol[mmsi]['marker'] = null;
                }
                if (this.eSymbol[mmsi].getRedCondition() == true) {
                    this.eSymbol[mmsi].setRedCondition(false);
                }
                this.manageMarker(mmsi);
            }
            if (this.cacheTheShip) {
                localStorage.setItem("shipinfo", JSON.stringify(this.shipinfo)); // Notice!
            }
        }
    }

    onAISD(mmsi, flag, data) {
        // console.log('D', mmsi, flag, data);
        // if(flag == 'R' || flag == 'X'){
        //     console.log(mmsi);
        // }
        const item = data;
        if ((mmsi in this.eSymbol) == false) {
            const code3 = parseInt(mmsi.toString().substr(0, 3));
            let nation = '???';
            if (code3 in MMSInation) {
                nation = MMSInation[code3];
            }
            this.eSymbol[mmsi] = new Enemy(item['lat'], item['lng'], item['sog'], item['cog'], item['status'], nation);
        } else {
            this.eSymbol[mmsi].update(item['lat'], item['lng'], item['sog'], item['cog'], item['status']);
        }
        if (mmsi in this.shipinfo) { // 先に動的情報を受信していた場合
            this.eSymbol[mmsi].haveStatic = true;
        }
        this.manageMarker(mmsi, flag);
        this.manageSound();
    }

    onReceived(message) {
        // console.log(message);
        const type = message['type'];
        const data = message['data'];

        if (type == 'GPS') {
            this.onGPS(data);
        } else if (type == 'AISD') {
            const mmsi = message['mmsi'];
            const flag = message['flag'];
            this.onAISD(mmsi, flag, data);
        } else if (type == 'AISS') {
            const mmsi = message['mmsi'];
            const mode = message['mode'];
            this.onAISS(mmsi, data, mode);
        } else {
            console.log(message);
        }
    }

}

