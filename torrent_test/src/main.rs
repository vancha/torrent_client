use lava_torrent::torrent::v1::Torrent;
use lava_torrent::tracker::TrackerResponse;
use std::path::Path;
use urlencoding::{encode, encode_binary};

use std::net::TcpStream;
use std::time::Duration;
//for use with the tcpstream
use std::io::Read;
use std::io::Write;

enum MessageType {
    KEEPALIVE,
    CHOKE,
    UNCHOKE,
    INTERESTED,
    NOT_INTERESTED,
    HAVE( Vec<u8>),//this vec will be 5 bytes in length
    PIECE(i32,i32,Vec<u8>),
    BITFIELD(Vec<u8>),
    REQUEST(Vec<u8>),
    PORT( i32),
}




impl MessageType {

    //<length prefix><message ID><payload>
    fn new(response: Vec<u8>) -> Self {
        println!("creating message type ");
        MessageType::KEEPALIVE
    }
}

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

    let peer_id = encode("thurmanmermanddddddd");
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
        match TcpStream::connect_timeout(&peer.addr, Duration::from_secs(5)) {
            Ok(mut stream) => {
                println!("Connected to server");
                //loop {
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

                    println!("handshake sent");
                    let mut handshake_buffer = [0u8; 68];
                    stream.read_exact(&mut handshake_buffer);
                    let their_info_hash = &handshake_buffer[28..48];
                    if info_hash != their_info_hash {
                        break;
                    } else {
                        println!("our infohashbrowns match, continuing conversation with peer.");
                    }
                    println!("handshake received");

                    let mut is_interested = false;
                    let mut is_choked = false;
                    
                    loop {

                        let mut size_buffer = [0u8; 4];
                        stream.read_exact(&mut size_buffer);
                        let message_size = i32::from_be_bytes(size_buffer);
                        
                        println!("size is {:?} ", size_buffer);
                        if message_size > 0 {
                            let mut payload_buffer =  vec![0u8; message_size as usize];
                            stream.read_exact(&mut payload_buffer);
                            //println!("payload is:  {:?}",payload_buffer);

                            let message_type = payload_buffer[0];

                            match message_type {
                                0 => {//choke
                                    println!("peer is choking us"); 
                                },
                                
                                1 => {//unchoke
                                      println!("peer is unchoking us");
                                },
                                2 => {//interested
                                      println!("peer is interested");

                                },
                                3 => {//not interested
                                      println!("peer is not interested");
                                },
                                4 => {//have
                                      println!("peer sent have message");
                                      println!("have is for piece with index {:?} out of {}",
                                               &payload_buffer[1..5],
                                               parsed_torrent.pieces.len());

                                      //lets just request the piece this peer has
                                      //this should be done by sendin a request message, before we
                                      //do this though we need to have sent an interested message
                                      //first, and additionally we must have received an unchoked
                                      //message
                                      //
                                      //after all that, we can send a request that looks like:
                                      //<4 byte length><1 byte msgid><4 byte piece index (0
                                      //based)><4 byte sub-piece index><4 byte sub-piece length
                                      //(probably 2^14>>
                                },
                                5 => {//bitfield
                                      println!("peer sent bitfield");
                                },
                                6 => {//request
                                    println!("peer sent request for block");
                                },
                                _ => {
                                    println!("peer sent something else that i don't understand.");
                                }
                            }

                        } else {
                            println!("peer sent keepalive message, ignoring.");
                        }
                        
                        
                    //}
                    //println!("contents of response: {:?}", read_buffer);
                    //let their_info_hash = &read_buffer[28..48];
                    //make sure hashes match, so we know that this peer and us are talking about
                    //the same file
                    //if info_hash == their_info_hash {
                    //    println!("our little info hashes match");
                    //}
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
