# ftp-server
> sockets based, threaded ftp server built in python

## Requirements

* python3

## How to use
To see example usage of the  server simply run:

```
make run
```

This will run the server on port 2121 and use a log file: **serverlog.txt**

To run using your own specified port and log file use the following convention:

```
python3 run.py <log-file> <port>
```

The server accepts 5 client connections at a time using threading. It supports the following commands: USER, PASS, CWD, CDUP, QUIT, PASV, EPSV, PORT, EPRT, RETR, STOR, PWD,
LIST.

The user accounts for the server are currently being read in from a json file called **credentials.json**. The syntax for this are as follows:

```
{
    "<username>" : "<pass>",
    "<username>" : "<pass>",
    ...
}
```

The log file for an example run can be found in the file **serverlog.txt**
