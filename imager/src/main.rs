#[macro_use] extern crate log;
extern crate log4rs;

extern crate pencil;
use pencil::{Pencil, Request, Response, PencilResult, PenHTTPError};
use pencil::http_errors::BadRequest;

#[macro_use] extern crate hyper;
use hyper::client::Client;

use std::io::Read;

extern crate url;
use url::form_urlencoded;

extern crate core;
use core::ops::Deref;

extern crate webdriver;
use webdriver::command::{WebDriverCommand, WebDriverMessage, NewSessionParameters, GetParameters, LocatorParameters};
use webdriver::common::{LocatorStrategy};
use webdriver::httpapi::{VoidWebDriverExtensionRoute};
use webdriver::error::{WebDriverResult, ErrorStatus, WebDriverError};
use webdriver::response;
use webdriver::response::{WebDriverResponse,NewSessionResponse,ValueResponse};
use std::collections::HashMap;
use std::time;
use std::thread;
use std::fs::File;
use std::io::Write;

extern crate rustc_serialize;
use rustc_serialize::json;
use rustc_serialize::json::Json;
use rustc_serialize::json::ToJson;
use rustc_serialize::base64::FromBase64Error;
use rustc_serialize::base64::FromBase64;

extern crate image;
use image::ImageBuffer;
use std::io::Cursor;

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

fn decode_response(json_str: &str) -> WebDriverResult<Json> {
	let decoded = Json::from_str(&json_str).unwrap();
	let status = decoded.find("status").expect("status code").as_u64().expect("numeric status code");
	let value = decoded.find("value").expect("value");
	return match status {
		0 => Ok(decoded.clone()),
		_ => {
			let message = value.find("message").expect("error message").as_string().expect("a string message").to_string();
			let kind = match status {
				7 => ErrorStatus::NoSuchElement,
				_ => ErrorStatus::UnknownError
			};
			return Err(WebDriverError::new(kind, message));
		}
	};
}

fn do_post(client: &mut hyper::client::Client, url: &str, body: &String) -> WebDriverResult<Json> {
	debug!("Request: {:?}", body);
	let mut res = client.post(url)
	    .body(body)
	    .send()
	    .unwrap();
	let mut buffer = String::new();
	res.read_to_string(&mut buffer).unwrap();
	debug!("Buffer: {}", buffer);
	//assert_eq!(res.status, hyper::Ok);
	let decoded = decode_response(&buffer);
	debug!("Decoded: {:?}", decoded);
	return decoded;
}

fn make_session(client: &mut hyper::client::Client) -> String {
	let mut mobile_emulation: json::Object = json::Object::new();
	mobile_emulation.insert("deviceName".to_string(), "Apple iPhone 5".to_json());
	let mut chrome_options: json::Object = json::Object::new();
	chrome_options.insert("mobileEmulation".to_string(), mobile_emulation.to_json());
	let mut desired: json::Object = json::Object::new();
	desired.insert("chromeOptions".to_string(), chrome_options.to_json());
	let mut request: json::Object = json::Object::new();
	request.insert("desiredCapabilities".to_string(), desired.to_json());
	let json_str = (&request).to_json().to_string();
	let decoded = do_post(client, "http://localhost:9516/session", &json_str);
	return decoded.expect("ok response").find("sessionId").expect("sessionId").as_string().expect("string session id").to_string();
}

fn delete_session(client: &mut hyper::client::Client, session_id: &String) {
	client.delete(&format!("http://localhost:9516/session/{}", session_id))
		.send()
		.unwrap();
}

fn goto_url(client: &mut hyper::client::Client, session_id: &String, url: String) {
	let params = GetParameters {url: url};
	client.post(&format!("http://localhost:9516/session/{}/url", session_id))
	    .body(&params.to_json().to_string())
	    .send()
	    .unwrap();
}

fn find_element_by_xpath(client: &mut hyper::client::Client, session_id: &String, xpath: String) -> WebDriverResult<WebDriverResponse> {
	let params = LocatorParameters{value: xpath.clone(), using: LocatorStrategy::XPath};
	let decoded = do_post(client, &format!("http://localhost:9516/session/{}/element", session_id), &params.to_json().to_string());
	return match decoded {
		Err(val) => Err(val),
		Ok(val) => Ok(WebDriverResponse::Generic(ValueResponse::new(val.find("value").expect("has value").clone())))
	};
}

fn get_for_element(client: &mut hyper::client::Client, session_id: &String, element: &ValueResponse, kind: &str) -> WebDriverResult<Json> {
	let element_id = element.value.find("ELEMENT").expect("ELEMENT").as_string().expect("String ELEMENT");
	let mut res = client.get(&format!("http://localhost:9516/session/{}/element/{}/{}", session_id, element_id, kind))
		.send()
		.unwrap();
	let mut buffer = String::new();
	res.read_to_string(&mut buffer).unwrap();
	debug!("Buffer: {}", buffer);
	//assert_eq!(res.status, hyper::Ok);
	let decoded = decode_response(&buffer);
	debug!("Decoded: {:?}", decoded);
	return decoded;
}

fn get_element_location(client: &mut hyper::client::Client, session_id: &String, element: &ValueResponse) -> WebDriverResult<Json> {
	return get_for_element(client, session_id, element, "location");
}

fn get_element_size(client: &mut hyper::client::Client, session_id: &String, element: &ValueResponse) -> WebDriverResult<Json> {
	return get_for_element(client, session_id, element, "size");
}

fn get_screenshot_as_png(client: &mut hyper::client::Client, session_id: &String) -> Result<Vec<u8>, FromBase64Error>{
	let mut res = client.get(&format!("http://localhost:9516/session/{}/screenshot", session_id))
		.send()
		.unwrap();
	let mut buffer = String::new();
	res.read_to_string(&mut buffer).unwrap();
	let decoded = decode_response(&buffer).expect("decoded");
	let value = decoded.find("value").expect("value").as_string().expect("string value");
	return value.clone().from_base64();
}

fn main() {
    log4rs::init_file("log.toml", Default::default()).unwrap();

	let mut client = Client::new();
	let session_id = make_session(&mut client);
	goto_url(&mut client, &session_id, "http://livestream.com/tinykittens/savina".to_string());
	thread::sleep(time::Duration::from_secs(5));
	let element: ValueResponse = match find_element_by_xpath(&mut client, &session_id, "//div[@id='image-container']/img".to_string()) {
		Err(val) => {
			warn!("Error while trying to get element: {:?}", val);
			Err(WebDriverError::new(ErrorStatus::UnknownError, val.to_json_string()))
		},
		Ok(val) => match val {
			WebDriverResponse::Generic(obj) => Ok(obj),
			_ => {
				warn!("Didn't expect {:?}", val);
				Err(WebDriverError::new(ErrorStatus::UnknownError, val.to_json_string()))
			}
		}
	}.unwrap();
	let element_location = get_element_location(&mut client, &session_id, &element).unwrap().find("value").expect("value").clone();
	let element_size = get_element_size(&mut client, &session_id, &element).unwrap().find("value").expect("value").clone();
	let screenshot = get_screenshot_as_png(&mut client, &session_id).unwrap();
	delete_session(&mut client, &session_id);

	let mut dump = File::create("foo.png").unwrap();
	dump.write(&screenshot).unwrap();

	let cursor = Cursor::new(&screenshot);
	let mut loaded_image = image::load(cursor, image::ImageFormat::PNG).unwrap();
	let cropped = loaded_image.crop(
		element_location.find("x").expect("x").as_u64().expect("numeric x") as u32,
		element_location.find("y").expect("y").as_u64().expect("numeric y") as u32,
		element_size.find("width").expect("width").as_u64().expect("numeric width") as u32,
		element_size.find("height").expect("height").as_u64().expect("numeric height") as u32);
	let mut cropped_file = File::create("cropped.png").unwrap();
	cropped.save(&mut cropped_file, image::ImageFormat::PNG).unwrap();

	//page_source(&mut client, &session_id);

    /*let mut app = Pencil::new("");
    app.set_debug(true);
    app.set_log_level();
    app.post("/streams", "streams", streams);
    app.run("127.0.0.1:8000");*/
}
