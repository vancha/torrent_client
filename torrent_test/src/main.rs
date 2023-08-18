use lava_torrent::torrent::v1::Torrent;
use lava_torrent::tracker::TrackerResponse;
use std::collections::HashMap;
use std::fs;
use std::path::Path;
use urlencoding::{encode, encode_binary};

use std::net::TcpStream;

//for use with the tcpstream
use std::io::Read;
use std::io::Write;

fn main() {
    /*
     * getting the data from the torrent file
     */
    let torrent_location = Path::new("/home/vancha/Documents/rust/torrent_test/ubuntu.torrent");

    let parsed_torrent = Torrent::read_from_file(torrent_location).unwrap();

    //here we have the announce url(s)
    let announce_url = parsed_torrent.announce.clone().unwrap();

    //here we have the info hash
    let info_hash = parsed_torrent.info_hash_bytes();
    let urlencoded_info_hash = encode_binary(&info_hash);
    println!("info hash: {:?}", info_hash);

    let peer_id = encode("thurmanmermadddddddn");
    let port = 6881;
    let uploaded = 0;
    let downloaded = 0;
    let left = parsed_torrent.length;
    let event = "started";

    /*
     * performing the request to the tracker for peers
     */
    let complete_request_url = format!("{announce_url}?info_hash={urlencoded_info_hash}&peer_id={peer_id}&port={port}&uploaded={uploaded}&downloaded={downloaded}&left={left}&event={event}");
    //client must announce himself by sending a get request to this tracker anounce url like
    //so: http://some.tracker.com:999/announce?info_hash=12345678901234567890&peer_id=ABCDEFGHIJKLMNOPQRST&ip=255.255.255.255&port=6881&downloaded=1234&left=98765&event=stopped
    //
    //in this response there is
    //here we perform the actual request
    let resp = reqwest::blocking::get(complete_request_url).unwrap();
    //if successful, this holds the tracker response, bencoded something that looks like this:

    let response_as_bytes = resp.bytes().unwrap();
    //println!("reponse as bytes: {:?}",response_as_bytes);
    let tracker_response =
        lava_torrent::tracker::TrackerResponse::from_bytes(response_as_bytes).unwrap();
    println!("tracker response: {:?}", tracker_response);

    println!(
        "nr. of pieces: {:?},total size in bytes: {}, without last piece it's {} in size",
        parsed_torrent.pieces.len(),
        parsed_torrent.length,
        (parsed_torrent.pieces.len() - 1) * parsed_torrent.piece_length as usize
    );

    /*
     * set up a tcp connection with those peers
     */

    let peers = match tracker_response {
        TrackerResponse::Success {
            interval,
            peers,
            warning,
            min_interval,
            tracker_id,
            complete,
            incomplete,
            extra_fields,
        } => {
            peers
            //println!("successfully retrieved all data from tracker, peers: {:?}", peers);
        }
        _ => {
            vec![]
            //println!("fail");
        }
    };

    for peer in peers {
        match TcpStream::connect(peer.addr) {
            Ok(mut stream) => {
                println!("Connected to server");
                loop {
                    //handshake: <pstrlen><pstr><reserved><info_hash><peer_id>
                    //for v1.0 of torrent protocol, pstrlen = 19 and pstr = BitTorrent protocol
                    let pstrlen = "19";
                    let pstr = "BitTorrent protocol";
                    let reserved = "00000000";
                    //info hash we have already defined above
                    //same for peer id

                    let mut request: Vec<u8> = [
                        &[0x13],
                        pstr.as_bytes(),
                        reserved.as_bytes(),
                        &info_hash,
                        &*peer_id.as_bytes(),
                    ]
                    .concat();
                    println!(
                        "request looks like: {:?}, and has size of {} bytes",
                        request,
                        request.len()
                    );
                    stream.write(&request);
                    let mut read_buffer = &mut [0; 128];
                    println!(
                        "The tcpstream responded with: {}",
                        stream.read(read_buffer).unwrap()
                    );
                    println!("contents of response: {:?}", read_buffer);
                    let their_info_hash = &read_buffer[28..48];
                    //make sure hashes match, so we know that this peer and us are talking about
                    //the same file
                    if info_hash == their_info_hash {
                        println!("our little info hashes match");
                    }
                    //break;
                }
            }
            Err(e) => {
                println!("Couldn't connect to server {} because {:?}", peer.addr, e);
            }
        }
    }
    /*
     *  perform handshakes with peers
     */

    /*
     *  download pieces
     */
}
