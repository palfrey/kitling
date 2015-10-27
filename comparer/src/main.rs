extern crate image;
extern crate img_hash;
extern crate postgres;
#[macro_use]
extern crate log;
extern crate log4rs;
extern crate time;
extern crate hyper;
extern crate url;
extern crate png;

use std::env;
use postgres::{Connection, SslMode};
use img_hash::{ImageHash, HashType};
use std::thread;
use std::default::Default;
use time::{Timespec, Duration};
use hyper::Client;
use hyper::header::ContentType;
use image::ImageFormat;
use std::io::Read;
use hyper::status::StatusCode;

fn main() {
    log4rs::init_file("log.toml", Default::default()).unwrap();
    let db_url: &str = &env::var("DATABASE_URL").unwrap();
    let conn = Connection::connect(db_url, &SslMode::None)
                .unwrap();

    loop {
        let stmt = conn.prepare("select * from videos_video order by \"lastRetrieved\" asc limit 1");
        if stmt.is_err() {
            error!("Error in prepare: {}", stmt.unwrap_err());
            thread::sleep_ms(4000);
            continue;
        }

        let ok_stmt = stmt.unwrap();
        let res = ok_stmt.query(&[]);
        if res.is_err() {
            error!("Error in query: {}", res.unwrap_err());
            thread::sleep_ms(4000);
            continue;
        }

        let items = res.unwrap();
        if items.len() == 0 {
            warn!("No video feeds");
            thread::sleep_ms(4000);
            continue;
        }
        let item = items.get(0);
        let url: String = item.get("url");
        let when: postgres::Result<Timespec> = item.get_opt("lastRetrieved");
        if when.is_err() {
            println!("Item: {}, When: never", url);
        }
        else {
            let now = time::now().to_timespec();
            let diff: Duration = now - when.unwrap();
            println!("Item: {}, When: {}", url, diff);
            if diff < Duration::minutes(1) {
                info!("oldest item is young: {}", diff);
                thread::sleep_ms(4000);
                continue;
            }
        }

        let mut options = vec![];
        options.push(("url".to_string(), url));
        let data: &str = &url::form_urlencoded::serialize(&options);

        let mut resp = Client::new()
            .post("http://imager:8000/streams")
            .header(ContentType::form_url_encoded())
            .body(data)
            .send().unwrap();

        if resp.status != StatusCode::Ok {
            warn!("{:?}", resp.status_raw());
            thread::sleep_ms(4000);
            continue;
        }

        let mut buf = Vec::new();
        resp.read_to_end(&mut buf).unwrap();
        let image = image::load_from_memory_with_format(&buf, ImageFormat::PNG).unwrap();
        let hash = ImageHash::hash(&image, 8, HashType::Gradient);

        println!("Image hash: {}", hash.to_base64());
        thread::sleep_ms(4000);

        //println!("% Difference: {}", hash1.dist_ratio(&hash2));
    }
}
