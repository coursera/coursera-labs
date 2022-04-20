# Using MySQL

## Using MySQL with vscode mysql extension
---
- The extension lives in the File Explorer Tab, in the MySQL section.
- Click the '+' icon. 
- When prompted for hostname and username, enter "localhost" and "root", respectively. Hit enter for everything else. You should see a new connection show up.
- To write a query, right-click on the database you want to use and select "New Query", or create a `.sql` file and prepend "USE" to any queries you with to run.
- To run the query, right-click the `.sql` file and select "Run MySQL Query".
- Right-click on the connection and select refresh to see database updates reflected.
- More details on the extension: [MySQL](https://marketplace.visualstudio.com/items?itemName=formulahendry.vscode-mysql)

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
