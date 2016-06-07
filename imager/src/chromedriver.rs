use hyper;
use webdriver::command::{GetParameters, LocatorParameters};
use webdriver::common::LocatorStrategy;
use webdriver::error::{WebDriverResult, ErrorStatus, WebDriverError};
use webdriver::response::{WebDriverResponse, ValueResponse};
use std::io::Read;
use std::ops::Drop;

use rustc_serialize::json;
use rustc_serialize::json::{Json, ToJson};
use rustc_serialize::base64::{FromBase64Error, FromBase64};

use std::process::{Command, Child};
use std::env;
use std::net::TcpStream;
use std::time;
use std::thread;

use std::sync::{Arc, Mutex, MutexGuard};
use nickel::{Request, Response, Middleware, Continue, MiddlewareResult};
use plugin::{Pluggable, Extensible};
use typemap::Key;

use rand;
use rand::Rng;

pub struct Webdriver {
    client: hyper::client::Client,
    host: String,
    port: u16,
    process: Child,
}

impl Default for Webdriver {
    fn default() -> Self {
        panic!("No good default for webdriver");
    }
}

pub struct WebdriverSession {
    client: hyper::client::Client,
    base_url: String,
    session_id: String,
}

fn decode_response(json_str: &str) -> WebDriverResult<Json> {
    let decoded = Json::from_str(&json_str).unwrap();
    let status =
        decoded.find("status").expect("status code").as_u64().expect("numeric status code");
    let value = decoded.find("value").expect("value");
    return match status {
        0 => Ok(decoded.clone()),
        _ => {
            let message = value.find("message")
                .expect("error message")
                .as_string()
                .expect("a string message")
                .to_string();
            let kind = match status {
                7 => ErrorStatus::NoSuchElement,
                _ => ErrorStatus::UnknownError,
            };
            return Err(WebDriverError::new(kind, message));
        }
    };
}

trait DoesPost {
    fn do_post(&self, url: String, body: &String) -> WebDriverResult<Json> {
        debug!("Request: {:?}", body);
        let mut res = self.client()
            .post(&url)
            .body(body)
            .send()
            .unwrap();
        let mut buffer = String::new();
        res.read_to_string(&mut buffer).unwrap();
        debug!("Buffer: {}", buffer);
        // assert_eq!(res.status, hyper::Ok);
        let decoded = decode_response(&buffer);
        debug!("Decoded: {:?}", decoded);
        return decoded;
    }

    fn client(&self) -> &hyper::client::Client;
}

impl Webdriver {
    pub fn new() -> Webdriver {
        let chromedriver_path = match env::var("CHROMEDRIVER") {
            Ok(val) => val,
            Err(_) => "./chromedriver".to_string(),
        };
        info!("Using {} as chromedriver path", chromedriver_path);


        let port: u16 = {
            let mut rng = rand::thread_rng();
            let mut candidate: u16;
            loop {
                candidate = rng.gen_range(2048, 65535);
                debug!("Candidate port {}", candidate);
                let stream = TcpStream::connect(("localhost", candidate));
                if stream.is_ok() {
                    debug!("Already used port {}", candidate);
                } else {
                    debug!("Good port {}", candidate);
                    break;
                }
            }
            candidate
        };

        let child = Command::new(&chromedriver_path)
            .arg(format!("--port={}", port))
            .spawn()
            .expect(&format!("spawning chromedriver from {}", &chromedriver_path));

        loop {
            let stream = TcpStream::connect(("localhost", port));
            if stream.is_ok() {
                debug!("Found chromedriver");
                break;
            } else {
                debug!("Can't connect to chromedriver yet");
                thread::sleep(time::Duration::from_secs(1));
            }
        }

        Webdriver {
            client: hyper::client::Client::new(),
            host: "localhost".to_string(),
            port: port,
            process: child,
        }
    }

    pub fn url(&self, rest: &str) -> String {
        format!("http://{}:{}/session{}", self.host, self.port, rest)
    }

    pub fn make_session(&self) -> WebdriverSession {
        let mut mobile_emulation: json::Object = json::Object::new();
        mobile_emulation.insert("deviceName".to_string(), "Apple iPhone 5".to_json());
        let mut chrome_options: json::Object = json::Object::new();
        chrome_options.insert("mobileEmulation".to_string(), mobile_emulation.to_json());
        chrome_options.insert("args".to_string(), ["--start-maximized".to_string(), "--no-sandbox".to_string()].to_json());
        let mut desired: json::Object = json::Object::new();
        desired.insert("chromeOptions".to_string(), chrome_options.to_json());
        let mut request: json::Object = json::Object::new();
        request.insert("desiredCapabilities".to_string(), desired.to_json());
        let json_str = (&request).to_json().to_string();
        let decoded = self.do_post(self.url(""), &json_str);
        let session_id = decoded.expect("ok response")
            .find("sessionId")
            .expect("sessionId")
            .as_string()
            .expect("string session id")
            .to_string();
        WebdriverSession {
            client: hyper::client::Client::new(),
            base_url: self.url(""),
            session_id: session_id,
        }
    }
}

impl Drop for Webdriver {
    fn drop(&mut self) {
        self.process.kill().unwrap();
        debug!("Killed chromedriver process");
    }
}

pub struct WebdriverMiddleware {
    pub mutex: Arc<Mutex<Webdriver>>,
}

impl WebdriverMiddleware {
    pub fn new(client: Webdriver) -> WebdriverMiddleware {
        WebdriverMiddleware { mutex: Arc::new(Mutex::new(client)) }
    }
}

impl<D> Middleware<D> for WebdriverMiddleware {
    fn invoke<'mw, 'conn>(&self,
                          req: &mut Request<'mw, 'conn, D>,
                          res: Response<'mw, D>)
                          -> MiddlewareResult<'mw, D> {
        req.extensions_mut().insert::<WebdriverMiddleware>(self.mutex.clone());
        Ok(Continue(res))
    }
}

impl Key for WebdriverMiddleware {
    type Value = Arc<Mutex<Webdriver>>;
}

pub trait WebdriverRequestExtensions {
    fn webdriver(&self) -> MutexGuard<Webdriver>;
}

impl<'a, 'b, D> WebdriverRequestExtensions for Request<'a, 'b, D> {
    fn webdriver(&self) -> MutexGuard<Webdriver> {
        self.extensions().get::<WebdriverMiddleware>().unwrap().lock().unwrap()
    }
}

impl DoesPost for Webdriver {
    fn client(&self) -> &hyper::client::Client {
        &self.client
    }
}
impl DoesPost for WebdriverSession {
    fn client(&self) -> &hyper::client::Client {
        &self.client
    }
}

impl Drop for WebdriverSession {
    fn drop(&mut self) {
        self.client()
            .delete(&self.url(format!("/{}", self.session_id)))
            .send()
            .unwrap();
    }
}

impl WebdriverSession {
    fn url(&self, rest: String) -> String {
        format!("{}{}", self.base_url, rest)
    }

    pub fn goto_url(&self, url: String) {
        let params = GetParameters { url: url };
        self.client()
            .post(&self.url(format!("/{}/url", self.session_id)))
            .body(&params.to_json().to_string())
            .send()
            .unwrap();
    }

    pub fn find_element_by_xpath(&self, xpath: String) -> WebDriverResult<WebDriverResponse> {
        let params = LocatorParameters {
            value: xpath.clone(),
            using: LocatorStrategy::XPath,
        };
        let decoded = self.do_post(self.url(format!("/{}/element", self.session_id)),
                                   &params.to_json().to_string());
        return match decoded {
            Err(val) => Err(val),
            Ok(val) => {
                Ok(WebDriverResponse::Generic(ValueResponse::new(val.find("value")
                    .expect("has value")
                    .clone())))
            }
        };
    }

    fn get_for_element(&self, element: &ValueResponse, kind: &str) -> WebDriverResult<Json> {
        let element_id =
            element.value.find("ELEMENT").expect("ELEMENT").as_string().expect("String ELEMENT");
        let mut res = self.client()
            .get(&self.url(format!("/{}/element/{}/{}", self.session_id, element_id, kind)))
            .send()
            .unwrap();
        let mut buffer = String::new();
        res.read_to_string(&mut buffer).unwrap();
        debug!("Buffer: {}", buffer);
        // assert_eq!(res.status, hyper::Ok);
        let decoded = decode_response(&buffer);
        debug!("Decoded: {:?}", decoded);
        return decoded;
    }

    pub fn get_element_location(&self, element: &ValueResponse) -> WebDriverResult<Json> {
        return self.get_for_element(element, "location");
    }

    pub fn get_element_size(&self, element: &ValueResponse) -> WebDriverResult<Json> {
        return self.get_for_element(element, "size");
    }

    pub fn get_element_attribute(&self, element: &ValueResponse, name: &str) -> String {
        return self.get_for_element(element, &format!("attribute/{}", name)).unwrap().find("value").expect("value").as_string().unwrap().to_string();
    }

    pub fn get_screenshot_as_png(&self) -> Result<Vec<u8>, FromBase64Error> {
        let mut res = self.client()
            .get(&self.url(format!("/{}/screenshot", self.session_id)))
            .send()
            .unwrap();
        let mut buffer = String::new();
        res.read_to_string(&mut buffer).unwrap();
        let decoded = decode_response(&buffer).expect("decoded");
        let value = decoded.find("value").expect("value").as_string().expect("string value");
        return value.clone().from_base64();
    }
}
