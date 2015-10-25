extern crate image;
extern crate img_hash;

use std::path::Path;
use img_hash::{ImageHash, HashType};

fn main() {
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
