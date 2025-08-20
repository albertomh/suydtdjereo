/**
 Usage:
 ```
 psql \
   -U $(whoami) \
   -d postgres \
   -v APP_USER_PASSWORD='password' \
   -f _db/set_up.sql
 ```
**/

BEGIN;
CREATE USER suydtdjereo WITH PASSWORD :'APP_USER_PASSWORD';
ALTER USER suydtdjereo CREATEDB;
COMMIT;

CREATE DATABASE suydtdjereo OWNER suydtdjereo;
