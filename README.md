# torrent_client
toy torrent downloader i'm trying to implement from scratch, please ignore this

important links for me: 

https://wiki.theory.org/BitTorrentSpecification
https://wiki.theory.org/BitTorrent_Tracker_Protocol

https://docs.rs/lava_torrent/0.11.1/lava_torrent/

https://byzantinemysteries.wordpress.com/2017/10/30/bittorrent-tracker-protocol-examples/

https://stackoverflow.com/questions/49180445/sending-bittorrent-http-request-to-ubuntu-tracker

https://foss.coep.org.in/coepwiki/index.php/Bittorrent_Client

https://docs.rs/reqwest/latest/reqwest/struct.Response.html#method.bytes

I've extracted the data from the torrent file, and managed to send a request to the url inside, using the lava_torrent crate. 


At this point i have received a respone from the announce tracker thingy, with the following data, indented here for readbility:

```
d
	8:complete
	i507e
	10:incomplete
	i16e
	8:interval
	i1800e
	5:peers
	l
		d
			2:ip
			19:2607:5300:60:623::1
			7:peer id
			20:-TR2940-bqvtv6y7pqj7
			4:port
			i51413e
		e
		d
			2:ip
			22:2a02:c206:3008:6973::1
			7:peer id
			20:-TR3000-c0axclo9rhkv
			4:port
			i51413e
		e
		d
			2:ip
			25:2a02:6f8:2020:203:3::1003
			7:peer id
			20:-TR3000-0lr7xdeum3fv
			4:port
			i51413e
		e
		d
			2:ip
			39:2403:6200:8840:8ddb:d513:1f69:1387:6b89
			7:peer id
			20:-FD51]�-m)(SMfzhQLRv
			4:port
			i49160e
		e
		d
			2:ip19:2001:41d0:a:62c9::17:peer id20:-TR3000-96rathvd2r094:porti60674eed2:ip35:2a01:e0a:bf1:53b0:7ee3:98:9a8b:70967:peer id20:-TR2940-a39kg9xj0rmc4:porti51413e
		e
		d
			2:ip20:2a01:4f8:241:4e4a::27:peer id20:-TR410Z-dlzcmrwpleff4:porti51413e
		e
		d
			2:ip14:185.125.190.597:peer id20:T03I--00S9efKsGa0kXV4:porti6899e
		e
		d
			2:ip39:2607:fea8:fdf0:80f1:3dce:e4fd:b934:e2c17:peer id20:-TR2940-fub0vk68m6id4:porti51413e
		e
		d
			2:ip21:2a01:260:1027:3::cef27:peer id20:-TR3000-zzfz4fwu2h0w4:porti33333e
		e
		d
			2:ip36:2a01:36d:115:c53e:f4eb:6ac:50d5:32617:peer id20:-UT2210-�b�(S����F-\u{17}4:porti13142e
		e
		d
			2:ip20:2607:5380:c002:1b::37:peer id20:-TR2940-ne8f3n0qlg8n4:porti51413e
		e
		d
			2:ip19:2001:41d0:8:d92e::17:peer id20:-TR2920-iu34apntk8yc4:porti51413e
		e
		d
			2:ip38:2a02:2698:902a:17fe:208:9bff:fece:443d7:peer id20:-TR2940-v8dpxv3vbwoa4:porti51413e
		e
		d
			2:ip19:2a01:4f8:10b:214::27:peer id20:-lt0D80-�P�ߎ�k�{�Ȅ4:porti6974e
		e
	e
e
```
Now to figure out what to do with this to actually download some stuff!

For the next step, i would like to add this stackoverflow comment that may offer insights in what to do now:

```


    You have peers and a tracker. All peers together at any given moment are the swarm. The usual situation is one or a few peers has the complete fileset and wishes to make it available to other peers.

    A peer acquires a .torrent file, which will have among other things A) the SHA-1 hash of the fileset, B) the URL of the tracker, and C) the number of pieces that the file is broken into, as well as an SHA-1 hash of every piece. The size of the pieces are determined by the torrent itself.

    The peer then connects to the tracker using the URL specified in the torrent. The tracker responds with a list of peers. Trackers talk HTTP over port 80 or 443.

    The peer then selects another peer, using the information from the tracker, and contacts it directly to set up an exchange session, attempting to get a piece. Note that exchange sessions are directly done by the peers and the tracker is NOT involved in the transfer. The tracker only provides information.

    Once the peer has a piece, it verifies it against the SHA-1 hash, and writes it to the file. It can then offer that piece when selecting another peer. Subsequent exchange sessions involve "trading" pieces. I believe peers will generally only give you the first piece if you have no other pieces.

    The peer reconsults the tracker every so often to get an updated list of peers. The peer does not have to wait for one exchange to finish before starting another one if it has multiple pieces, so once the peer has a bunch of pieces the transfer can really speed up. This is why torrents start slow but gain speed quickly as the peer acquires pieces.

    When a peer has all the pieces, the entire file is verified against the fileset SHA-1 hash. Then, it becomes a seeder, and is now doing nothing but helping the fileset be more highly available. Peers that do not have all the pieces are leechers.

    If a torrent has no seeds, it is dead, although if a complete copy of the file exists between all pieces held by all peers they will eventually trade to get a complete copy amongst themselves.

    The SHA-1 hash is how the tracker and peers "know" which file is supposed to be swarmed. Filenames in the torrent aren't used to identify the data. Pieces that don't verify against the hases in the .torrent file are thrown out. Peers that continually send bad pieces are snubbed by other peers and will eventually not be able to connect to anyone in the swarm.

    A smaller piece size means the torrent is more robust since peers can trade pieces quicker, but it also means more hashes of pieces in the .torrent file have to be listed and therefore the .torrent file can be large.

    If you are publishing something via BitTorrent, it's best to seed the file as long as you wish to make it available. Other peers will be helping you, since most BitTorrent software implements algorithms that favor trying to spread things among as many peers as possible to maximize conncurrent connections. In this way BitTorrent can help you publish things and save bandwidth costs.

```
