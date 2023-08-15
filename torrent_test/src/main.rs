use std::path::Path;
use std::fs;
use std::collections::HashMap;
use lava_torrent::torrent::v1::Torrent;
use urlencoding::{encode_binary, encode};



fn main() {
    let torrent_location = Path::new("/home/vancha/Documents/rust/torrent_test/ubuntu.torrent");   
    
    let parsed_torrent = Torrent::read_from_file(torrent_location).unwrap();

    //here we have the announce url(s)
    let announce_url    = parsed_torrent.announce.clone().unwrap();

    //here we have the info hash
    let info_hash       = parsed_torrent.info_hash_bytes();
    let urlencoded_info_hash = encode_binary(&info_hash);
    println!("info hash: {:?}", info_hash);
    
    let peer_id = encode("thurmanmermadddddddn");
    let port = 6881;
    let uploaded = 0;
    let downloaded = 0;
    let left = parsed_torrent.length;
    let event = "started";

    let complete_request_url = format!("{announce_url}?info_hash={urlencoded_info_hash}&peer_id={peer_id}&port={port}&uploaded={uploaded}&downloaded={downloaded}&left={left}&event={event}");
    //client must announce himself by sending a get request to this tracker anounce url like
    //so: http://some.tracker.com:999/announce?info_hash=12345678901234567890&peer_id=ABCDEFGHIJKLMNOPQRST&ip=255.255.255.255&port=6881&downloaded=1234&left=98765&event=stopped
    //here we perform the actual request 
    let resp = reqwest::blocking::get(complete_request_url).unwrap(); 
    //if successful, this holds the tracker response, bencoded something that looks like this:
    /*
     * "d8:completei507e10:incompletei16e8:intervali1800e5:peersld2:ip19:2607:5300:60:623::17:peer id20:-TR2940-bqvtv6y7pqj74:porti51413eed2:ip22:2a02:c206:3008:6973::17:peer id20:-TR3000-c0axclo9rhkv4:porti51413eed2:ip25:2a02:6f8:2020:203:3::10037:peer id20:-TR3000-0lr7xdeum3fv4:porti51413eed2:ip39:2403:6200:8840:8ddb:d513:1f69:1387:6b897:peer id20:-FD51]�-m)(SMfzhQLRv4:porti49160eed2:ip19:2001:41d0:a:62c9::17:peer id20:-TR3000-96rathvd2r094:porti60674eed2:ip35:2a01:e0a:bf1:53b0:7ee3:98:9a8b:70967:peer id20:-TR2940-a39kg9xj0rmc4:porti51413eed2:ip20:2a01:4f8:241:4e4a::27:peer id20:-TR410Z-dlzcmrwpleff4:porti51413eed2:ip14:185.125.190.597:peer id20:T03I--00S9efKsGa0kXV4:porti6899eed2:ip39:2607:fea8:fdf0:80f1:3dce:e4fd:b934:e2c17:peer id20:-TR2940-fub0vk68m6id4:porti51413eed2:ip21:2a01:260:1027:3::cef27:peer id20:-TR3000-zzfz4fwu2h0w4:porti33333eed2:ip36:2a01:36d:115:c53e:f4eb:6ac:50d5:32617:peer id20:-UT2210-�b�(S����F-\u{17}4:porti13142eed2:ip20:2607:5380:c002:1b::37:peer id20:-TR2940-ne8f3n0qlg8n4:porti51413eed2:ip19:2001:41d0:8:d92e::17:peer id20:-TR2920-iu34apntk8yc4:porti51413eed2:ip38:2a02:2698:902a:17fe:208:9bff:fece:443d7:peer id20:-TR2940-v8dpxv3vbwoa4:porti51413eed2:ip19:2a01:4f8:10b:214::27:peer id20:-lt0D80-�P�ߎ�k�{�Ȅ4:porti6974eeee"
     */

    let response_as_bytes =  resp.bytes().unwrap();
    println!("reponse as bytes: {:?}",response_as_bytes);
    let tracker_response = lava_torrent::tracker::TrackerResponse::from_bytes(response_as_bytes);
    println!("tracker response: {:?}", tracker_response);
}
