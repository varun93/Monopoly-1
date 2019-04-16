const properties = [
    {
    "id":0,
    "class":"corner go",
    "name":"Go",
    "instructions": "Collect $200.00 salary as you pass"
    },
    {
    "id":1,
    "class":"street",
    "name":"Med. Avenue",
    "monopoly":"brown",
    "price":60,
    "build_cost":50,
    "rent":2,
    "rent_house_1":10,
    "rent_house_2":30,
    "rent_house_3":90,
    "rent_house_4":160,
    "rent_hotel":250
    },
    {
    "id":2,
    "class":"chest",
    "name":"Community Chest",
    "instructions": "Follow instructions on top card"
    },
    {
    "id":3,
    "class":"street",
    "name":"Baltic Avenue",
    "monopoly":"brown",
    "price":60,
    "build_cost":50,
    "rent":4,
    "rent_house_1":20,
    "rent_house_2":60,
    "rent_house_3":180,
    "rent_house_4":320,
    "rent_hotel":450
    },
    {
    "id":4,
    "class":"income-tax",
    "name":"Income Tax",
    "tax":200
    },
    {
    "id":5,
    "class":"railroad",
    "name":"Reading Railroad",
    "monopoly":"railroad",
    "price":200,
    "rent":25
    },
    {
    "id":6,
    "class":"street",
    "name":"Oriental Avenue",
    "monopoly":"light-blue",
    "price":100,
    "build_cost":50,
    "rent":6,
    "rent_house_1":30,
    "rent_house_2":90,
    "rent_house_3":270,
    "rent_house_4":400,
    "rent_hotel":550
    },
    {
    "id":7,
    "class":"chance",
    "name":"Chance",
    "instructions": "Follow instructions on top card"
    },
    {
    "id":8,
    "class":"street",
    "name":"Vermont Avenue",
    "monopoly":"light-blue",
    "price":100,
    "build_cost":50,
    "rent":6,
    "rent_house_1":30,
    "rent_house_2":90,
    "rent_house_3":270,
    "rent_house_4":400,
    "rent_hotel":550
    },
    {
    "id":9,
    "class":"street",
    "name":"Connecticut Avenue",
    "monopoly":"light-blue",
    "price":120,
    "build_cost":50,
    "rent":8,
    "rent_house_1":40,
    "rent_house_2":100,
    "rent_house_3":300,
    "rent_house_4":450,
    "rent_hotel":600
    },
    {
    "id":10,
    "class":"corner jail",
    "name":"Jail"
    },
    {
    "id":11,
    "class":"street",
    "name":"St. Charles Place",
    "monopoly":"pink",
    "price":140,
    "build_cost":100,
    "rent":10,
    "rent_house_1":50,
    "rent_house_2":150,
    "rent_house_3":450,
    "rent_house_4":625,
    "rent_hotel":750
    },
    {
    "id":12,
    "class":"utility electric-company",
    "name":"Electric Company",
    "monopoly":"utility",
    "price":150,
    "rent":4
    },
    {
    "id":13,
    "class":"street",
    "name":"States Avenue",
    "monopoly":"pink",
    "price":140,
    "build_cost":100,
    "rent":10,
    "rent_house_1":50,
    "rent_house_2":150,
    "rent_house_3":450,
    "rent_house_4":625,
    "rent_hotel":750
    },
    {
    "id":14,
    "class":"street",
    "name":"Virginia Avenue",
    "monopoly":"pink",
    "price":160,
    "build_cost":100,
    "rent":12,
    "rent_house_1":60,
    "rent_house_2":180,
    "rent_house_3":500,
    "rent_house_4":700,
    "rent_hotel":900
    },
    {
    "id":15,
    "class":"railroad",
    "name":"Penn Railroad",
    "monopoly":"railroad",
    "price":200,
    "rent":25
    },
    {
    "id":16,
    "class":"street",
    "name":"St. James Place",
    "monopoly":"orange",
    "price":180,
    "build_cost":100,
    "rent":14,
    "rent_house_1":70,
    "rent_house_2":200,
    "rent_house_3":550,
    "rent_house_4":750,
    "rent_hotel":950
    },
    {
    "id":17,
    "class":"chest",
    "name":"Community Chest",
    "instructions": "Follow instructions on top card"
    },
    {
    "id":18,
    "class":"street",
    "name":"Tennessee Avenue",
    "monopoly":"orange",
    "price":180,
    "build_cost":100,
    "rent":14,
    "rent_house_1":70,
    "rent_house_2":200,
    "rent_house_3":550,
    "rent_house_4":750,
    "rent_hotel":950
    },
    {
    "id":19,
    "class":"street",
    "name":"New York Avenue",
    "monopoly":"orange",
    "price":200,
    "build_cost":100,
    "rent":16,
    "rent_house_1":80,
    "rent_house_2":220,
    "rent_house_3":600,
    "rent_house_4":800,
    "rent_hotel":1000
    },
    {
    "id":20,
    "class":"corner free-parking",
    "name":"Free Parking"
    },
    {
    "id":21,
    "class":"street",
    "name":"Kentucky Avenue",
    "monopoly":"red",
    "price":220,
    "build_cost":150,
    "rent":18,
    "rent_house_1":90,
    "rent_house_2":250,
    "rent_house_3":700,
    "rent_house_4":875,
    "rent_hotel":1050
    },
    {
    "id":22,
    "class":"chance",
    "name":"Chance",
    "instructions": "Follow instructions on top card"
    },
    {
    "id":23,
    "class":"street",
    "name":"Indiana Avenue",
    "monopoly":"red",
    "price":220,
    "build_cost":150,
    "rent":18,
    "rent_house_1":90,
    "rent_house_2":250,
    "rent_house_3":700,
    "rent_house_4":875,
    "rent_hotel":1050
    },
    {
    "id":24,
    "class":"street",
    "name":"Illinois Avenue",
    "monopoly":"red",
    "price":240,
    "build_cost":150,
    "rent":20,
    "rent_house_1":100,
    "rent_house_2":300,
    "rent_house_3":750,
    "rent_house_4":925,
    "rent_hotel":1100
    },
    {
    "id":25,
    "class":"railroad",
    "name":"B. & O. Railroad",
    "monopoly":"railroad",
    "price":200,
    "rent":25
    },
    {
    "id":26,
    "class":"street",
    "name":"Atlantic Avenue",
    "monopoly":"yellow",
    "price":260,
    "build_cost":150,
    "rent":22,
    "rent_house_1":110,
    "rent_house_2":330,
    "rent_house_3":800,
    "rent_house_4":975,
    "rent_hotel":1150
    },
    {
    "id":27,
    "class":"street",
    "name":"Ventnor Avenue",
    "monopoly":"yellow",
    "price":260,
    "build_cost":150,
    "rent":22,
    "rent_house_1":110,
    "rent_house_2":330,
    "rent_house_3":800,
    "rent_house_4":975,
    "rent_hotel":1150
    },
    {
    "id":28,
    "class":"utility waterworks",
    "name":"Water Works",
    "monopoly":"utility",
    "price":150,
    "rent":4
    },
    {
    "id":29,
    "class":"street",
    "name":"Marvin Gardens",
    "monopoly":"yellow",
    "price":280,
    "build_cost":150,
    "rent":24,
    "rent_house_1":120,
    "rent_house_2":360,
    "rent_house_3":850,
    "rent_house_4":1025,
    "rent_hotel":1200
    },
    {
    "id":30,
    "class":"go-to-jail",
    "name":"Go To Jail"
    },
    {
    "id":31,
    "class":"street",
    "name":"Pacific Avenue",
    "monopoly":"green",
    "price":300,
    "build_cost":200,
    "rent":26,
    "rent_house_1":130,
    "rent_house_2":390,
    "rent_house_3":900,
    "rent_house_4":1100,
    "rent_hotel":1275
    },
    {
    "id":32,
    "class":"street",
    "name":"North Carolina Avenue",
    "monopoly":"green",
    "price":300,
    "build_cost":200,
    "rent":26,
    "rent_house_1":130,
    "rent_house_2":390,
    "rent_house_3":900,
    "rent_house_4":1100,
    "rent_hotel":1275
    },
    {
    "id":33,
    "class":"chest",
    "name":"Community Chest"
    },
    {
    "id":34,
    "class":"street",
    "name":"Penn Avenue",
    "monopoly":"green",
    "price":320,
    "build_cost":200,
    "rent":28,
    "rent_house_1":150,
    "rent_house_2":450,
    "rent_house_3":1000,
    "rent_house_4":1200,
    "rent_hotel":1400
    },
    {
    "id":35,
    "class":"railroad",
    "name":"Short Line",
    "monopoly":"railroad",
    "price":200,
    "build_cost":0,
    "rent":25
    },
    {
    "id":36,
    "class":"chance",
    "name":"Chance"
    },
    {
    "id":37,
    "class":"street",
    "name":"Park Place",
    "monopoly":"dark-blue",
    "price":350,
    "build_cost":200,
    "rent":35,
    "rent_house_1":175,
    "rent_house_2":500,
    "rent_house_3":1100,
    "rent_house_4":1300,
    "rent_hotel":1500
    },
    {
    "id":38,
    "class":"luxury-tax",
    "name":"Luxury Tax",
    "tax":100
    },
    {
    "id":39,
    "class":"street",
    "name":"Boardwalk",
    "monopoly":"dark-blue",
    "price":400,
    "build_cost":200,
    "rent":50,
    "rent_house_1":200,
    "rent_house_2":600,
    "rent_house_3":1400,
    "rent_house_4":1700,
    "rent_hotel":2000
    }
    ];
    
    export default properties;