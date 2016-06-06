#[macro_use]
extern crate log;
extern crate log4rs;

#[macro_use]
extern crate nickel;
use nickel::{Request, Response, MiddlewareResult, Nickel, MediaType};
use nickel::status::StatusCode;
use nickel::router::http_router::HttpRouter;

#[macro_use]
extern crate hyper;
use hyper::header::ContentLength;

use std::io::Read;

extern crate url;
use url::form_urlencoded;

extern crate webdriver;
use webdriver::response::{WebDriverResponse, ValueResponse};

use std::time;
use std::thread;

extern crate core;

extern crate rustc_serialize;

extern crate image;
use image::GenericImage;
use std::io::Cursor;

extern crate get_if_addrs;

extern crate plugin;
extern crate typemap;

mod chromedriver;
use chromedriver::WebdriverRequestExtensions;

use core::ops::Deref;
extern crate rand;

fn streams<'a, D>(request: &mut Request<D>, mut res: Response<'a, D>) -> MiddlewareResult<'a, D> {
    let session = request.webdriver().deref().make_session();
    let mut buffer = String::new();
    request.origin.read_to_string(&mut buffer).unwrap();
    let mut parse = form_urlencoded::parse(buffer.as_bytes());
    let mut url = match parse.find(|k| k.0 == "url") {
        Some((_, value)) => value.into_owned(),
        None => return res.error(StatusCode::BadRequest, "No URL in request"),

    };
    let request_url = match url::Url::parse(&url) {
        Ok(value) => value,
        Err(_) => {
            return res.error(StatusCode::BadRequest,
                             format!("Request URL was dodgy: '{}'", url))
        }

    };
    let host = request_url.host_str().unwrap();
    let xpath = match host {
            "livestream.com" => "//div[@id='image-container']/img",
            "www.ustream.tv" => "//video[@id='UViewer']",
            "www.youtube.com" => {
                url = url + "?autoplay=1";
                "//div[@id='player']"
            }
            _ => {
                return res.error(StatusCode::BadRequest,
                                 format!("Request URL host ({}) wasn't in known list: '{}'",
                                         host,
                                         url))
            }

        }
        .to_string();

    session.goto_url(url);
    thread::sleep(time::Duration::from_secs(5));
    let element: ValueResponse = match session.find_element_by_xpath(xpath) {
        Err(val) => {
            return res.error(StatusCode::BadRequest,
                             format!("Error while trying to get element: {:?}", val))
        }
        Ok(val) => {
            match val {
                WebDriverResponse::Generic(obj) => obj,
                _ => return res.error(StatusCode::BadRequest, format!("Didn't expect {:?}", val)),
            }
        }
    };
    let element_location = {
        let loc = session.get_element_location(&element);
        loc.unwrap()
            .find("value")
            .expect("value")
            .clone()
    };
    let element_size = {
        let size = session.get_element_size(&element);
        size.unwrap()
            .find("value")
            .expect("value")
            .clone()
    };
    let screenshot = {
        let png = session.get_screenshot_as_png();
        png.unwrap()
    };

    let cursor = Cursor::new(&screenshot);
    let mut loaded_image = image::load(cursor, image::ImageFormat::PNG).unwrap();
    let (width, height) = loaded_image.dimensions();
    debug!("Loaded image dimensions: {} x {}", width, height);
    let cropped = loaded_image.crop(
		element_location.find("x").expect("x").as_u64().expect("numeric x") as u32,
		element_location.find("y").expect("y").as_u64().expect("numeric y") as u32,
		element_size.find("width").expect("width").as_u64().expect("numeric width") as u32,
		element_size.find("height").expect("height").as_u64().expect("numeric height") as u32);

    let mut output_buffer: Vec<u8> = Vec::new();
    cropped.save(&mut output_buffer, image::ImageFormat::PNG).unwrap();
    res.set(MediaType::Png);
    res.set(ContentLength(output_buffer.len() as u64));
    res.send(output_buffer)
}

fn run(ip: std::net::IpAddr, port: u16, client: chromedriver::Webdriver) {
    let mut server = Nickel::new();
    // app.set_debug(true);
    // app.set_log_level();
    server.utilize(chromedriver::WebdriverMiddleware::new(client));
    server.post("/streams", streams);
    server.listen((ip, port));
}

fn main() {
    log4rs::init_file("log.toml", Default::default()).unwrap();
    let port = 8000;
    let mut handles = Vec::new();
    for iface in get_if_addrs::get_if_addrs().unwrap() {
        handles.push(::std::thread::spawn(move || {
            let client = chromedriver::Webdriver::new();
            let ip = iface.ip();
            info!("Listening on {}:{} for {}", ip, port, iface.name);
            run(ip, port, client);
        }));
    }

    info!("All listeners spawned");

    for handle in handles {
        handle.join().unwrap();
    }
}
