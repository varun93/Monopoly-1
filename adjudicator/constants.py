"""TODO:Ensure board can't be modified by agents""" 

board = {
-1:{
"class":"Jail",
"name":"Jail",
"monopoly":"None",
"monopoly_size":0,
"price":0,
"build_cost":0,
"rent":[0,0,0,0,0,0],
"tax":0
},
0:{
"class":"Idle",
"name":"Go",
"monopoly":"None",
"monopoly_size":0,
"price":0,
"build_cost":0,
"rent":[0,0,0,0,0,0],
"tax":0
},
1:{
"class":"Street",
"name":"Mediterranean Avenue",
"monopoly":"Brown",
"monopoly_size":2,
"price":60,
"build_cost":50,
"rent":[2,10,30,90,160,250],
"tax":0,
"monopoly_group_elements":[3],
"monopoly_group_id": 0
},
2:{
"class":"Chest",
"name":"Community Chest",
"monopoly":"None",
"monopoly_size":0,
"price":0,
"build_cost":0,
"rent":[0,0,0,0,0,0],
"tax":0
},
3:{
"class":"Street",
"name":"Baltic Avenue",
"monopoly":"Brown",
"monopoly_size":2,
"price":60,
"build_cost":50,
"rent":[4,20,60,180,320,450],
"tax":0,
"monopoly_group_elements":[1],
"monopoly_group_id": 0
},
4:{
"class":"Tax",
"name":"Income Tax",
"monopoly":"None",
"monopoly_size":0,
"price":0,
"build_cost":0,
"rent":[0,0,0,0,0,0],
"tax":200
},
5:{
"class":"Railroad",
"name":"Reading Railroad",
"monopoly":"Railroad",
"monopoly_size":4,
"price":200,
"build_cost":0,
"rent":[25,50,100,200,0,0],
"tax":0,
"monopoly_group_elements":[15, 25, 35],
"monopoly_group_id": 1
},
6:{
"class":"Street",
"name":"Oriental Avenue",
"monopoly":"Light Blue",
"monopoly_size":3,
"price":100,
"build_cost":50,
"rent":[6,30,90,270,400,550],
"tax":0,
"monopoly_group_elements":[8, 9],
"monopoly_group_id": 2
},
7:{
"class":"Chance",
"name":"Chance",
"monopoly":"None",
"monopoly_size":0,
"price":0,
"build_cost":0,
"rent":[0,0,0,0,0,0],
"tax":0
},
8:{
"class":"Street",
"name":"Vermont Avenue",
"monopoly":"Light Blue",
"monopoly_size":3,
"price":100,
"build_cost":50,
"rent":[6,30,90,270,400,550],
"tax":0,
"monopoly_group_elements":[6, 9],
"monopoly_group_id": 2
},
9:{
"class":"Street",
"name":"Connecticut Avenue",
"monopoly":"Light Blue",
"monopoly_size":3,
"price":120,
"build_cost":50,
"rent":[8,40,100,300,450,600],
"tax":0,
"monopoly_group_elements":[6, 8],
"monopoly_group_id": 2
},
10:{
"class":"Idle",
"name":"Jail",
"monopoly":"None",
"monopoly_size":0,
"price":0,
"build_cost":0,
"rent":[0,0,0,0,0,0],
"tax":0
},
11:{
"class":"Street",
"name":"St. Charles Place",
"monopoly":"Pink",
"monopoly_size":3,
"price":140,
"build_cost":100,
"rent":[10,50,150,450,625,750],
"tax":0,
"monopoly_group_elements":[13, 14],
"monopoly_group_id": 3
},
12:{
"class":"Utility",
"name":"Electric Company",
"monopoly":"Utility",
"monopoly_size":2,
"price":150,
"build_cost":0,
"rent":[4,10,0,0,0,0],
"tax":0,
"monopoly_group_elements":[28],
"monopoly_group_id": 4
},
13:{
"class":"Street",
"name":"States Avenue",
"monopoly":"Pink",
"monopoly_size":3,
"price":140,
"build_cost":100,
"rent":[10,50,150,450,625,750],
"tax":0,
"monopoly_group_elements":[11, 14],
"monopoly_group_id": 3
},
14:{
"class":"Street",
"name":"Virginia Avenue",
"monopoly":"Pink",
"monopoly_size":3,
"price":160,
"build_cost":100,
"rent":[12,60,180,500,700,900],
"tax":0,
"monopoly_group_elements":[11, 13],
"monopoly_group_id": 3
},
15:{
"class":"Railroad",
"name":"Pennsylvania Railroad",
"monopoly":"Railroad",
"monopoly_size":4,
"price":200,
"build_cost":0,
"rent":[25,50,100,200,0,0],
"tax":0,
"monopoly_group_elements":[5, 25, 35],
"monopoly_group_id": 1
},
16:{
"class":"Street",
"name":"St. James Place",
"monopoly":"Orange",
"monopoly_size":3,
"price":180,
"build_cost":100,
"rent":[14,70,200,550,750,950],
"tax":0,
"monopoly_group_elements":[18, 19],
"monopoly_group_id": 5
},
17:{
"class":"Chest",
"name":"Community Chest",
"monopoly":"None",
"monopoly_size":0,
"price":0,
"build_cost":0,
"rent":[0,0,0,0,0,0],
"tax":0
},
18:{
"class":"Street",
"name":"Tennessee Avenue",
"monopoly":"Orange",
"monopoly_size":3,
"price":180,
"build_cost":100,
"rent":[14,70,200,550,750,950],
"tax":0,
"monopoly_group_elements":[16, 19],
"monopoly_group_id": 5
},
19:{
"class":"Street",
"name":"New York Avenue",
"monopoly":"Orange",
"monopoly_size":3,
"price":200,
"build_cost":100,
"rent":[16,80,220,600,800,1000],
"tax":0,
"monopoly_group_elements":[16, 18],
"monopoly_group_id": 5
},
20:{
"class":"Idle",
"name":"Free Parking",
"monopoly":"None",
"monopoly_size":0,
"price":0,
"build_cost":0,
"rent":[0,0,0,0,0,0],
"tax":0
},
21:{
"class":"Street",
"name":"Kentucky Avenue",
"monopoly":"Red",
"monopoly_size":3,
"price":220,
"build_cost":150,
"rent":[18,90,250,700,875,1050],
"tax":0,
"monopoly_group_elements":[23, 24],
"monopoly_group_id": 6
},
22:{
"class":"Chance",
"name":"Chance",
"monopoly":"None",
"monopoly_size":0,
"price":0,
"build_cost":0,
"rent":[0,0,0,0,0,0],
"tax":0
},
23:{
"class":"Street",
"name":"Indiana Avenue",
"monopoly":"Red",
"monopoly_size":3,
"price":220,
"build_cost":150,
"rent":[18,90,250,700,875,1050],
"tax":0,
"monopoly_group_elements":[21, 24],
"monopoly_group_id": 6
},
24:{
"class":"Street",
"name":"Illinois Avenue",
"monopoly":"Red",
"monopoly_size":3,
"price":240,
"build_cost":150,
"rent":[20,100,300,750,925,1100],
"tax":0,
"monopoly_group_elements":[21, 23],
"monopoly_group_id": 6
},
25:{
"class":"Railroad",
"name":"B. & O. Railroad",
"monopoly":"Railroad",
"monopoly_size":4,
"price":200,
"build_cost":0,
"rent":[25,50,100,200,0,0],
"tax":0,
"monopoly_group_elements":[5, 15, 35],
"monopoly_group_id": 1
},
26:{
"class":"Street",
"name":"Atlantic Avenue",
"monopoly":"Yellow",
"monopoly_size":3,
"price":260,
"build_cost":150,
"rent":[22,110,330,800,975,1150],
"tax":0,
"monopoly_group_elements":[27, 29],
"monopoly_group_id": 7
},
27:{
"class":"Street",
"name":"Ventnor Avenue",
"monopoly":"Yellow",
"monopoly_size":3,
"price":260,
"build_cost":150,
"rent":[22,110,330,800,975,1150],
"tax":0,
"monopoly_group_elements":[26, 29],
"monopoly_group_id": 7
},
28:{
"class":"Utility",
"name":"Water Works",
"monopoly":"Utility",
"monopoly_size":2,
"price":150,
"build_cost":0,
"rent":[4,10,0,0,0,0],
"tax":0,
"monopoly_group_elements":[12],
"monopoly_group_id": 4
},
29:{
"class":"Street",
"name":"Marvin Gardens",
"monopoly":"Yellow",
"monopoly_size":3,
"price":280,
"build_cost":150,
"rent":[24,120,360,850,1025,1200],
"tax":0,
"monopoly_group_elements":[26, 27],
"monopoly_group_id": 7
},
30:{
"class":"GoToJail",
"name":"Go To Jail",
"monopoly":"None",
"monopoly_size":0,
"price":0,
"build_cost":0,
"rent":[0,0,0,0,0,0],
"tax":0
},
31:{
"class":"Street",
"name":"Pacific Avenue",
"monopoly":"Green",
"monopoly_size":3,
"price":300,
"build_cost":200,
"rent":[26,130,390,900,1100,1275],
"tax":0,
"monopoly_group_elements":[32, 34],
"monopoly_group_id": 8
},
32:{
"class":"Street",
"name":"North Carolina Avenue",
"monopoly":"Green",
"monopoly_size":3,
"price":300,
"build_cost":200,
"rent":[26,130,390,900,1100,1275],
"tax":0,
"monopoly_group_elements":[31, 34],
"monopoly_group_id": 8
},
33:{
"class":"Chest",
"name":"Community Chest",
"monopoly":"None",
"monopoly_size":0,
"price":0,
"build_cost":0,
"rent":[0,0,0,0,0,0],
"tax":0
},
34:{
"class":"Street",
"name":"Pennsylvania Avenue",
"monopoly":"Green",
"monopoly_size":3,
"price":320,
"build_cost":200,
"rent":[28,150,450,1000,1200,1400],
"tax":0,
"monopoly_group_elements":[31, 32],
"monopoly_group_id": 8
},
35:{
"class":"Railroad",
"name":"Short Line",
"monopoly":"Railroad",
"monopoly_size":4,
"price":200,
"build_cost":0,
"rent":[25,50,100,200,0,0],
"tax":0,
"monopoly_group_elements":[5, 15, 25],
"monopoly_group_id": 1
},
36:{
"class":"Chance",
"name":"Chance",
"monopoly":"None",
"monopoly_size":0,
"price":0,
"build_cost":0,
"rent":[0,0,0,0,0,0],
"tax":0
},
37:{
"class":"Street",
"name":"Park Place",
"monopoly":"Dark Blue",
"monopoly_size":2,
"price":350,
"build_cost":200,
"rent":[35,175,500,1100,1300,1500],
"tax":0,
"monopoly_group_elements":[39],
"monopoly_group_id": 9
},
38:{
"class":"Tax",
"name":"Luxury Tax",
"monopoly":"None",
"monopoly_size":0,
"price":0,
"build_cost":0,
"rent":[0,0,0,0,0,0],
"tax":100
},
39:{
"class":"Street",
"name":"Boardwalk",
"monopoly":"Dark Blue",
"monopoly_size":2,
"price":400,
"build_cost":200,
"rent":[50,200,600,1400,1700,2000],
"tax":0,
"monopoly_group_elements":[37],
"monopoly_group_id": 9
}
}

communityChestCards = [
  {
    "id": 0,
    "content": "Advance to Go (Collect $200)",
    "type": 3,
    "position": 1,
    "money": 0,
    "money2": 0
  },
  {
    "id": 1,
    "content": "Bank error in your favor, collect $200",
    "type": 1,
    "position": 0,
    "money": 200,
    "money2": 0
  },
  {
    "id": 2,
    "content": "Doctor's fees, Pay $50",
    "type": 1,
    "position": 0,
    "money": -50,
    "money2": 0
  },
  {
    "id": 3,
    "content": "From sale of stock you get $50",
    "type": 1,
    "position": 0,
    "money": 50,
    "money2": 0
  },
  {
    "id": 4,
    "content": "Get out of jail free, this card may be kept until needed",
    "type": 4,
    "position": 0,
    "money": 0,
    "money2": 0
  },
  {
    "id": 5,
    "content": "Go to jail, go directly to jail - Do not pass Go, do not collect $200",
    "type": 3,
    "position": -1,
    "money": 0,
    "money2": 0
  },
  {
    "id": 6,
    "content": "Grand Opera Night. Collect $50 from every player for opening night seats.",
    "type": 2,
    "position": 0,
    "money": 50,
    "money2": 0
  },
  {
    "id": 7,
    "content": "Holiday Fund matures - Receive $100",
    "type": 1,
    "position": 0,
    "money": 100,
    "money2": 0
  },
  {
    "id": 8,
    "content": "Income Tax refund. Collect $20",
    "type": 1,
    "position": 0,
    "money": 20,
    "money2": 0
  },
  {
    "id": 9,
    "content": "Life Insurance Matures - Collect $100",
    "type": 1,
    "position": 0,
    "money": 100,
    "money2": 0
  },
  {
    "id": 10,
    "content": "Pay Hospital Fees of $50",
    "type": 1,
    "position": 0,
    "money": -50,
    "money2": 0
  },
  {
    "id": 11,
    "content": "Pay School Fees of $50",
    "type": 1,
    "position": 0,
    "money": -50,
    "money2": 0
  },
  {
    "id": 12,
    "content": "Receive $25 Consultancy Fee",
    "type": 1,
    "position": 0,
    "money": 25,
    "money2": 0
  },
  {
    "id": 13,
    "content": "You are assessed for street repairs: Pay $40 per house and $115 per hotel you own.",
    "type": 5,
    "position": 0,
    "money": -40,
    "money2": -115
  },
  {
    "id": 14,
    "content": "You have won second prize in a beauty contest - collect $10",
    "type": 1,
    "position": 0,
    "money": 10,
    "money2": 0
  },
  {
    "id": 15,
    "content": "You inherit $100",
    "type": 1,
    "position": 0,
    "money": 100,
    "money2": 0
  }
]

chanceCards = [
  {
    "id": 0,
    "content": "Advance to Go (Collect $200)",
    "type": 3,
    "position": 1,
    "money": 0,
    "money2": 0
  },
  {
    "id": 1,
    "content": "Advance to Illinois Ave. If you pass Go, collect $200.",
    "type": 3,
    "position": 25,
    "money": 0,
    "money2": 0
  },
  {
    "id": 2,
    "content": "Advance to St. Charles Place. If you pass Go, collect $200",
    "type": 3,
    "position": 12,
    "money": 0,
    "money2": 0
  },
  {
    "id": 3,
    "content": "Advance token to nearest Utility. If unowned, you may buy it from the Bank. If owned, throw dice and pay owner a total 10 times the amount thrown.",
    "type": 7,
    "position": 0,
    "money": 0,
    "money2": 0
  },
  {
    "id": 4,
    "content": "Advance token to the nearest Railroad and pay owner twice the rental to which he/she {he} is otherwise entitled. If Railroad is unowned, you may buy it from the Bank",
    "type": 6,
    "position": 0,
    "money": 0,
    "money2": 0
  },
  {
    "id": 5,
    "content": "Advance token to the nearest Railroad and pay owner twice the rental to which he/she {he} is otherwise entitled. If Railroad is unowned, you may buy it from the Bank",
    "type": 6,
    "position": 0,
    "money": 0,
    "money2": 0
  },
  {
    "id": 6,
    "content": "Bank pays you dividend of $50",
    "type": 1,
    "position": 0,
    "money": 50,
    "money2": 0
  },
  {
    "id": 7,
    "content": "Get out of Jail free, this card may be kept until needed, or traded",
    "type": 4,
    "position": 0,
    "money": 0,
    "money2": 0
  },
  {
    "id": 8,
    "content": "Go Back 3 Spaces",
    "type": 8,
    "position": 0,
    "money": 0,
    "money2": 0
  },
  {
    "id": 9,
    "content": "Go to Jail. Go directly to Jail. Do not pass GO, do not collect $200.",
    "type": 3,
    "position": -1,
    "money": 0,
    "money2": 0
  },
  {
    "id": 10,
    "content": "Make general repairs on all your property: For each house pay $25, For each hotel pay $100.",
    "type": 5,
    "position": 0,
    "money": -25,
    "money2": -100
  },
  {
    "id": 11,
    "content": "Pay poor tax of $15",
    "type": 1,
    "position": 0,
    "money": -15,
    "money2": 0
  },
  {
    "id": 12,
    "content": "Take a trip to Reading Railroad.",
    "type": 3,
    "position": 6,
    "money": 0,
    "money2": 0
  },
  {
    "id": 13,
    "content": "Advance to Boardwalk",
    "type": 3,
    "position": 40,
    "money": 0,
    "money2": 0
  },
  {
    "id": 14,
    "content": "You have been elected chairman of the board, pay each player $50",
    "type": 2,
    "position": 0,
    "money": -50,
    "money2": 0
  },
  {
    "id": 15,
    "content": "Your building loan matures, collect $150",
    "type": 1,
    "position": 0,
    "money": 150,
    "money2": 0
  }
]

state_history = []
