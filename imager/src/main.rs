#[macro_use] extern crate log;
extern crate log4rs;

extern crate pencil;
use pencil::{Pencil, Request, Response, PencilResult};

#[macro_use] extern crate hyper;
use hyper::header::ContentLength;

use std::io::Read;

extern crate url;
use url::form_urlencoded;

extern crate core;
use core::ops::Deref;

fn hello(request: &mut Request) -> PencilResult {
    let length = {
		let ref req = request.request;
		req.headers.get::<ContentLength>().unwrap().deref();
	};
    println!("{:?}", length);
    let mut buffer = String::new();
    request.request.read_to_string(&mut buffer);
	println!("{:?}", buffer);
	let mut parse = form_urlencoded::parse(buffer.as_bytes());
	println!("{:?}", parse.find(|k| k.0 == "url"));
    Ok(Response::from("Hello World!"))
}

fn main() {
    log4rs::init_file("log.toml", Default::default()).unwrap();
    let mut app = Pencil::new("/web/hello");
    app.set_debug(true);
    app.set_log_level();
    app.post("/", "hello", hello);
    app.run("127.0.0.1:8000");
}
