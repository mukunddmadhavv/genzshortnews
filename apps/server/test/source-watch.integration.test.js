import {test} from 'node:test';
import {promisify} from 'node:util';
import {execFile} from 'node:child_process';
import pg from 'pg';

test('source automation uses a durable transactional ledger and verified webhook',{timeout:30000},async()=>{
 const name=`genz_source_test_${Date.now()}`;
 const url=new URL(process.env.TEST_DATABASE_URL || 'postgresql://localhost:55432/postgres');
 const admin=new pg.Client({connectionString:url.href});await admin.connect();
 try {
  await admin.query(`CREATE DATABASE ${name}`);url.pathname=`/${name}`;
  const {stdout}=await promisify(execFile)(process.execPath,[new URL('./source-watch-fixture.mjs',import.meta.url).pathname],{env:{...process.env,DATABASE_URL:url.href},timeout:25000});
  console.log(stdout.trim());
 } finally {await admin.query(`DROP DATABASE IF EXISTS ${name} WITH (FORCE)`);await admin.end();}
});
