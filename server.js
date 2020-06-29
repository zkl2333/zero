const Koa = require("koa");

// 注意require('koa-router')返回的是函数:
const router = require("koa-router")();

const app = new Koa();

const rpio = require("rpio");
const POWER_CHECK = 7;

// logger
app.use(async (ctx, next) => {
	await next();
	const rt = ctx.response.get("X-Response-Time");
	console.log(`${ctx.method} ${ctx.url} - ${rt}`);
});

// x-response-time
app.use(async (ctx, next) => {
	const start = Date.now();
	await next();
	const ms = Date.now() - start;
	ctx.set("X-Response-Time", `${ms}ms`);
});

// add url-route:
router.get("/power-check", async (ctx, next) => {
	ctx.response.body = rpio.read(POWER_CHECK);
});

router.get("/", async (ctx, next) => {
	ctx.response.body = "你好";
});

// add router middleware:
app.use(router.routes());

app.listen(3000);
console.log("app started at port 3000...");
