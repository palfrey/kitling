#[macro_use] extern crate log;
extern crate log4rs;

extern crate pencil;
use pencil::{Pencil, Request, Response, PencilResult, PenHTTPError};
use pencil::http_errors::BadRequest;

#[macro_use] extern crate hyper;
use hyper::header::ContentLength;

use std::io::Read;

extern crate url;
use url::form_urlencoded;

extern crate core;
use core::ops::Deref;

fn streams(request: &mut Request) -> PencilResult {
	let mut buffer = String::new();
	request.request.read_to_string(&mut buffer);
	let mut parse = form_urlencoded::parse(buffer.as_bytes());
	let url = match parse.find(|k| k.0 == "url") {
		Some((_, value)) => value,
		None => return Err(PenHTTPError(BadRequest))
	};
    Ok(Response::from("Hello World!"))
}

fn main() {
    log4rs::init_file("log.toml", Default::default()).unwrap();
    let mut app = Pencil::new("");
    app.set_debug(true);
    app.set_log_level();
    app.post("/streams", "streams", streams);
    app.run("127.0.0.1:8000");
}
