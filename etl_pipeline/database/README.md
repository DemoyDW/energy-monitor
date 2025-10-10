# Description

The database folder contains the scripts to initialise the database needed and also to seed the database with the master data.


# Usage

## Connecting And Running schema

``` sh
psql -h <host> -p <port> -U <username> -d <database> -f schema.sql

- Input Password

```


## Connecting And Seeding Data

``` sh
psql -h <host> -p <port> -U <username> -d <database> -f seed.sql

- Input Password

```