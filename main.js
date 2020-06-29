var rpio = require("rpio");
const POWER_CHECK = 7;

rpio.open(POWER_CHECK, rpio.INPUT);
console.log("电源 " + (rpio.read(POWER_CHECK) == 1 ? "连接" : "断开"));

let state = rpio.read(POWER_CHECK);

function pollcb(pin) {
	rpio.msleep(300);
	if (rpio.read(POWER_CHECK) != state) {
		state = rpio.read(POWER_CHECK);
		console.log("电源 " + (state == 1 ? "连接" : "断开"));
	} else {
		return;
	}
}

rpio.poll(POWER_CHECK, pollcb);
