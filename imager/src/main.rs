#[macro_use]
extern crate log;
extern crate log4rs;

extern crate pencil;
use pencil::{Pencil, Request, Response, PencilResult, PenHTTPError};
use pencil::http_errors::BadRequest;

#[macro_use]
extern crate hyper;

use std::io::Read;

extern crate url;
use url::form_urlencoded;

extern crate webdriver;
use webdriver::response::{WebDriverResponse, ValueResponse};
use std::time;
use std::thread;
use std::fs::File;
use std::io::Write;

extern crate rustc_serialize;

extern crate image;
use std::io::Cursor;

extern crate get_if_addrs;

mod chromedriver;

fn streams(request: &mut Request) -> PencilResult {
    let client = chromedriver::Webdriver::new();
    let session = client.make_session();

    let mut buffer = String::new();
    request.request.read_to_string(&mut buffer).unwrap();
    let mut parse = form_urlencoded::parse(buffer.as_bytes());
    let url = match parse.find(|k| k.0 == "url") {
        Some((_, value)) => value.into_owned(),
        None => return Err(PenHTTPError(BadRequest)),
    };
    session.goto_url(url);
    thread::sleep(time::Duration::from_secs(5));
    let element: ValueResponse =
        match session.find_element_by_xpath("//div[@id='image-container']/img".to_string()) {
            Err(val) => {
                warn!("Error while trying to get element: {:?}", val);
                return Err(PenHTTPError(BadRequest));
            }
            Ok(val) => {
                match val {
                    WebDriverResponse::Generic(obj) => obj,
                    _ => {
                        warn!("Didn't expect {:?}", val);
                        return Err(PenHTTPError(BadRequest));
                    }
                }
            }
        };
    let element_location =
        session.get_element_location(&element).unwrap().find("value").expect("value").clone();
    let element_size =
        session.get_element_size(&element).unwrap().find("value").expect("value").clone();
    let screenshot = session.get_screenshot_as_png().unwrap();

    let mut dump = File::create("foo.png").unwrap();
    dump.write(&screenshot).unwrap();

    let cursor = Cursor::new(&screenshot);
    let mut loaded_image = image::load(cursor, image::ImageFormat::PNG).unwrap();
    let cropped = loaded_image.crop(
		element_location.find("x").expect("x").as_u64().expect("numeric x") as u32,
		element_location.find("y").expect("y").as_u64().expect("numeric y") as u32,
		element_size.find("width").expect("width").as_u64().expect("numeric width") as u32,
		element_size.find("height").expect("height").as_u64().expect("numeric height") as u32);

    let mut output_buffer: Vec<u8> = Vec::new();
    cropped.save(&mut output_buffer, image::ImageFormat::PNG).unwrap();
    let mut response = Response::from(output_buffer);
    response.set_content_type("image/png");
    Ok(response)
}

fn make_app() -> Pencil {
    let mut app = Pencil::new("");
    app.set_debug(true);
    app.set_log_level();
    app.post("/streams", "streams", streams);
    return app;
}

fn main() {
    log4rs::init_file("log.toml", Default::default()).unwrap();
    let port = 8000;
    let mut handles = Vec::new();
    for iface in get_if_addrs::get_if_addrs().unwrap() {
        handles.push(::std::thread::spawn(move || {
            let ip = iface.ip();
            let app = make_app();
            info!("Listening on {}:{} for {}", ip, port, iface.name);
            app.run((ip, port));
        }));
    }

    info!("All listeners spawned");

    for handle in handles {
        handle.join().unwrap();
    }
}
