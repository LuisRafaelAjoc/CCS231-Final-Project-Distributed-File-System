# Run this file with port number to create server.
# Format: python server.py {port_number}
# Example: python server.py 8001 | Will create a server with address "127.0.0.1" and port 8001

import sys
from server_module import ServerNode

port = int(sys.argv[1])
ServerNode("127.0.0.1", port).run()