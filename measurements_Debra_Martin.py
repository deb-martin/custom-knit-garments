# enter body measurements and heights here in cm
# figure out a way to pass the person's name
person = "Debra Martin"
body_data = {
	# "name":			"Debra Martin",
	"floor":			{"meas": 80,		"height": -105,	"circumferential": True},
	"belowCalves":		{"meas": 80,		"height": -88,	"circumferential": True},
	"aboveCalves":		{"meas": 83,		"height": -73,	"circumferential": True},
	"belowKnees":		{"meas": 83,		"height": -67,	"circumferential": True},
	"aboveKnees":		{"meas": 93,		"height": -57,	"circumferential": True},
	"midThighs":		{"meas": 100,		"height": -44,	"circumferential": True},
	"fullThighs":		{"meas": 111,		"height": -40,	"circumferential": True},
	"seatDepth":		{"meas": 112,		"height": -27,	"circumferential": True},
	"lowHip":			{"meas": 110,		"height": -17,	"circumferential": True},
	"highHip":			{"meas": 98,		"height": -12,	"circumferential": True},
	"waist":			{"meas": 77,		"height": 0,	"circumferential": True},
	"underBust":		{"meas": 84,		"height": 10,	"circumferential": True},
	"fullBust":			{"meas": 97,		"height": 19,	"circumferential": True},
	"highBust":			{"meas": 90,		"height": 29,	"circumferential": True}, 	# 8cm is half body depth at highest armpit which is also highBust on me 22cm down from shoulder at neck 29 + 22 = 51
	"underArm1":		{"meas": 40,		"height": 29,	"circumferential": False}, 	# across chest
	"underArm2":		{"meas": 34,		"height": 31,	"circumferential": False}, 	# across chest
	"underArm3":		{"meas": 32,		"height": 43,	"circumferential": False},
	"outerShoulder":	{"meas": 96,		"height": 38,	"circumferential": True}, 	# outer shoulder
	"shoulderNeck":		{"meas": 38,		"height": 47,	"circumferential": True}, 	# shoulder length is 17.5 cm delta height is 9 cm slope is  ((17.5)^2 - (9)^2))^0.5 =15
	"frontNeck":		{"meas": 38,		"height": 36,	"circumferential": True},
	"backNeck":			{"meas": 38,		"height": 44,	"circumferential": True}
	}
