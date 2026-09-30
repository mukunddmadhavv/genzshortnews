// Preserve the pre-existing tunnel's origin port while Studio runs on 6969.
import net from 'node:net';
const server=net.createServer(client=>{
 const upstream=net.connect(6969,'127.0.0.1');
 client.pipe(upstream);upstream.pipe(client);
 client.on('error',()=>upstream.destroy());upstream.on('error',()=>client.destroy());
 client.on('close',()=>upstream.destroy());upstream.on('close',()=>client.destroy());
});
server.listen(2021,'127.0.0.1');
