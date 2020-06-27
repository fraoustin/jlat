# JLAT

You can create a referentiel of note for your lecture.

You have to create

- one or more book
- one or more viewer
- one or more note

## Usage by docker

    docker run -d -v <localpath>:/data --name mapit -p 5000:80 fraoustin/jlat

You can used the environment:

- JLAT_PORT default 5000
- JLAT_DEBUG default false
- JLAT_HOST default 0.0.0.0
- JLAT_DIR default /data

## Migration 1 to 2

add columns in database

> ALTER TABLE user ADD COLUMN apikey VARCHAR;
> ALTER TABLE user ADD COLUMN token VARCHAR;

> ALTER TABLE book ADD COLUMN email VARCHAR;
> ALTER TABLE book ADD COLUMN phone VARCHAR;
> ALTER TABLE book ADD COLUMN nationality VARCHAR;
> ALTER TABLE book ADD COLUMN address VARCHAR;
> ALTER TABLE book ADD COLUMN fileurl VARCHAR;
> ALTER TABLE book ADD COLUMN filepdf VARCHAR;
> ALTER TABLE book ADD COLUMN fileepub VARCHAR;
> ALTER TABLE book ADD COLUMN trad_lastname VARCHAR;
> ALTER TABLE book ADD COLUMN trad_firstname VARCHAR;
> ALTER TABLE book ADD COLUMN trad_email VARCHAR;
> ALTER TABLE book ADD COLUMN trad_phone VARCHAR;
> ALTER TABLE book ADD COLUMN trad_nationality VARCHAR;
> ALTER TABLE book ADD COLUMN trad_address VARCHAR;

Create dir files/archives