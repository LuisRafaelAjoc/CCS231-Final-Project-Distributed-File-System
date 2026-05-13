# CCS231-Final-Project-Distributed-File-System
A simple Python implementation of an simulated distributed file system. In final fulfillment of the requirements for the course CCS 231: Parallel and Distributed Computing.

## Group Members:
- Ajoc, Luis Rafael L.
- Alvarez, Jan Daniel O.
- Barlas, Ramuel Carl Q.
- Robles, John Felmer B.

## Dependencies:
- Python 3.14
- socket
- threading
- time
- copy
- json
- sys

## Instructions for Running
The order of initialization for a server or the client is irrelevant; both are capable of handling the absence of one another. However, both the client and at least one server must be running to perform operations.
### Client
- In a terminal, run `python client.py`
### Server
- Open 3 new terminals
- For each terminal, run:
  - `python server.py 8001`
  - `python server.py 8002`
  - `python server.py 8003`

## Instructions for Performing Operations
Note: To perform operations, the client and at least one server must be running
### List Directory Contents
- To read root directory contents, type `list` in client terminal
- To read contents of specific directories, type `list {directory pathname}`
### Read File
- To read a file, type `read {file pathname}` in client terminal
### Write File
- To write/overwrite a file, type `write {file pathname} {content}` in client terminal

Note: The system will automatically create new directories if the the file path has directories that the file system currently do not have
### Delete File
- To delete a file, type `delete {file pathname}` in client terminal
### Show Cache
- To show the client's current cache, type `showcache` in client terminal
### Exit Program
- To exit the client, type `exit` in client terminal

## Instructions for Testing DFS Resilience
- To simulate a server crash, select a server and type `Ctrl + C`
- As long as one server remains available, the file system will remain up to date
- Crashed servers that have recovered will sync using the file system of the available server

Note: The servers do not have persistent storage. If all 'crash' and initialized once more, the file system will be at the initial state
