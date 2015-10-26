extern crate image;
extern crate img_hash;
extern crate postgres;
#[macro_use]
extern crate log;
extern crate log4rs;

use std::env;
use postgres::{Connection, SslMode};
use std::path::Path;
use img_hash::{ImageHash, HashType};
use std::thread;
use std::default::Default;

fn main() {
    log4rs::init_file("log.toml", Default::default()).unwrap();
    let url: &str = &env::var("DATABASE_URL").unwrap();
    let conn = Connection::connect(url, &SslMode::None)
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
        println!("Item: {}", items.get(0).columns().first().unwrap().name());

        let image1 = image::open(&Path::new("image1.png")).unwrap();
        let image2 = image::open(&Path::new("image2.png")).unwrap();

        // These two lines produce hashes with 64 bits (8 ** 2),
        // using the Gradient hash, a good middle ground between
        // the performance of Mean and the accuracy of DCT.
        let hash1 = ImageHash::hash(&image1, 8, HashType::Gradient);
        let hash2 = ImageHash::hash(&image2, 8, HashType::Gradient);

        println!("Image1 hash: {}", hash1.to_base64());
        println!("Image2 hash: {}", hash2.to_base64());

        println!("% Difference: {}", hash1.dist_ratio(&hash2));
    }
}
