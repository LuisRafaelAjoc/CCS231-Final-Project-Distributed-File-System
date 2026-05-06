# CCS231-Final-Project-Distributed-File-System
A simple Python implementation of an simulated distributed file system. In final fulfillment of the requirements for the course CCS 231: Parallel and Distributed Computing.

## Group Members:
- Ajoc, Luis Rafael L.
- Alvarez, Jan Daniel O.
- Barlas, Ramuel Carl Q.
- Robles, John Felmer B.

## Dependencies:
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
- In a terminal, run `python server.py {port_number}`. Replace `port_number` with your chosen port.
