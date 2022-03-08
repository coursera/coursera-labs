# Using MySQL

## Using MySQL with vscode mysql extension
---
- Connect to mysql server by clicking the database icon in the left menu bar.
- Select `Add new connection`, then select `MySQL`.
- Connect to mysql server with the following settings:
``` 
    Connection name: (Anything)
    Connect Using: Server and Port
    Server Address: localhost
    Port: 3306
    Database: (Your database name)
    Username: root (or coder)
    Use password: Use empty password
```
- Click Save Connection, then Connect Now, you will see a `.sql` file opened in the editor.
- Write your SQL queries in this file, then click Run on active connection to run this query.
- More details on the extension:  [SQLTools](https://marketplace.visualstudio.com/items?itemName=mtxr.sqltools)

<br/>

## Using MySQL from the command line
----
- Open a terminal, run the command `mysql` .
- You can now type in sql commands to interact with mysql server.

<br/><br/>

## Instructors: Populate the database for a new lab
---
- **DON'T modify mysql data directory (`/var/lib/mysql/`) directly.**
- Create a new lab, upload your data files (csv files, sql dump files etc.) and sql files to `/home/coder/project` (or any other mount point that is not `/var/lib/mysql`).
- Open the instructor lab, an empty mysql server should already be running in the background.
- Populate the database by running your sql queries, database changes will automatically be saved and made available to students when lab is published.

<br/><br/>

### Miscellaneous
---
- To restart the mysql server: find the pid for mysqld by `ps -aux | grep mysqld`, then `kill {pid}` to stop the server , `mysqld` to start the server.
- When creating a new sql users, create it with `IDENTIFIED WITH mysql_native_password` so that this user can work with the vscode mysql extension, or else you can only use this user from the command line mysql client.
