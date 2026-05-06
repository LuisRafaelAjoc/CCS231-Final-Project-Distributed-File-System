import socket
import threading
import time
import json
import copy

# Hardcoded server addresses and ports
# Can handle more than 3 separate servers, just add more tuples in the list and run more servers
# Format: ("127.0.0.1", port_number). Note: port_number must be int, and greater than 1024
SERVERS = [
    ("127.0.0.1", 8001),
    ("127.0.0.1", 8002),
    ("127.0.0.1", 8003),
    # ("127.0.0.1", 8004),
]

# Initial contents of hierarchical file system
INITIAL_FS = {
    "type": "directory",
    "children": {
        "finance": {
            "type": "directory",
            "children": {
                "budget.txt": {"type": "file", "content": "Finance budget report"},
                "expenses.txt": {"type": "file", "content": "Expense breakdown"},
                "subdirectory": {
                    "type": "directory",
                    "children": {
                        "budget.txt": {"type": "file", "content": "Finance budget report (Sub Dir)"},
                        "expenses.txt": {"type": "file", "content": "Expense breakdown (Sub Dir)"}
                    }
                },
            }
        },
        "hr": {
            "type": "directory",
            "children": {
                "employees.txt": {"type": "file", "content": "Employee list"},
                "policies.txt": {"type": "file", "content": "HR policies"},
                "subdirectory": {
                    "type": "directory",
                    "children": {}
                },
            }
        }
    }
}

# ---Helper functions---
# Logging function. For keeping track of what is happening in a server
def log(port, msg):
    print(f"[{port}] {msg}")

# Server health check
def is_alive(server):
    try:
        with socket.create_connection(server, timeout=1) as s:
            s.sendall(b"PING")              # Send PING to server
            s.recv(1024)                    # If server is alive, will respond with PONG
        return True
    except:
        return False

# Function for finding main
def find_main():
    for server in SERVERS:
        # The first from SERVERS list that is online automatically becomes main
        if is_alive(server):
            return server
    return None

# Class for initializing a server.
class ServerNode:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.fs = copy.deepcopy(INITIAL_FS)             # Initialize simulated file system
        
        # The main server is the firstmost online server based on the hardcoded list
        # For example, if the second server in the list is the first online server, it 
        # becomes main. But if the server that precedes it in the list becomes online, 
        # the preceding server becomes main and the second server becomes a replica
        self.is_main = False       
        self.replica_conns = []                     # Keep track of connections with replicas to replicate changes

    
    # ---File operations---
    # Read file function
    # Input: path to requested file
    def read_file(self, path):
        current_node = self.fs                          # Start with root

        # Get every directory and the requested file from file path input
        # For item in the path, assign it as the current node
        for component in path.strip("/").split("/"):
            # Retrieve the dictionary representing the directory from current node if it exists and assign it as current node. 
            current_node = current_node["children"].get(component)

            # If the directory does not exist, return error
            if not current_node:
                return "ERROR"

        return current_node['content']

    # Write file function
    # Input: file path of file, content of file
    def write_file(self, path, content):
        current_node = self.fs                          # Start with root
        file_path = path.strip("/").split("/")              # Create array with every separated directory and the filename

        # For every directory in the file path input
        for component in file_path[:-1]:
            # Retrieve the dictionary representing the directory from current node if it exists and assign it as current node. 
            # If not, create a new dictionary to represent directory and assign to current node.
            current_node = current_node["children"].setdefault(component, {"type": "directory", "children": {}})

        # In the last directory, create new dictionary representing file
        # If the file already exists, the value of content is overwritten
        current_node["children"][file_path[-1]] = {"type": "file", "content": content}

        # # The current node is now the requested file. Return content
        # return current_node[file_path[-1]]["content"]

    # Delete file function
    # Input: path to requested file
    def delete_file(self, path):
        current_node = self.fs                          # Start with root
        file_path = path.strip("/").split("/")              # Create array with every separated directory and the filename
        
        # For every directory in the file path input
        for component in file_path[:-1]:
            # Retrieve the dictionary representing the directory from current node if it exists and assign it as current node. 
            current_node = current_node["children"].get(component)

            # If the directory does not exist, return error
            if not current_node:
                return "ERROR"
            
        # In the last directory, remove the requested file from its children
        current_node["children"].pop(file_path[-1], None)

    # List directory contents function
    # Input: path to requested directory
    def list_dir(self, path):
        current_node = self.fs                                  # Start with root

        # If the path is not root
        if path != "/":
            # Create array with every separated directory
            directories = path.strip("/").split("/")

            # For every directory in path input
            for dir in directories:
                # Get it from current node, and assign as new current node
                current_node = current_node["children"].get(dir)
                
                # If the directory does not exist, return error
                if not current_node:
                    return "ERROR"
    
        dir_content = []

        # key = name of directory; value = metadata (type, children)
        # For every child in the directory
        for key, value in current_node["children"].items():
            if value["type"] == "directory":
                dir_content.append(key + "/")      # If a directory, append '/'
            else:
                dir_content.append(key)            # If it is a file, just append

        result = "\n".join(dir_content)             # Turn into list separated by newline

        if result == "":
            return "(empty)"
        else:
            return result

    # Functions related to replication
    # Replication loop process
    def replica_connector_loop(self):
        while True:
            for server in SERVERS:
                # If server is the current server, ignore
                if server == (self.host, self.port):
                    continue

                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)        # Create TCP socket
                    sock.settimeout(1)
                    sock.connect(server)

                    # If the connection is not in the list of replica connections, add it
                    if sock not in self.replica_conns:
                        self.replica_conns.append(sock)
                        log(self.port, f"CONNECTED TO REPLICA {server[1]}")

                except:
                    pass

            time.sleep(3)       # Suspend process for 3 seconds

    # Function for server replication
    def replicate(self, msg):
        # For every connected server replica
        for connections in self.replica_conns:
            # Send command to be replicated
            try:
                connections.sendall(msg.encode())
            except:
                pass

    # Function for syncing file system contents
    # Used by replicas to sync their file systems with that of main server
    def sync_from_main(self):
        main = find_main()

        # If the server itself is the main server or main server currently does not exist, exit function
        if main == (self.host, self.port) or not main:
            return

        # Try to sync with main server
        try:
            log(self.port, "SYNCING FROM MAIN")
            with socket.create_connection(main) as conn:
                conn.sendall(b"SYNC")
                self.fs = json.loads(conn.recv(100000).decode())
            log(self.port, "SYNC COMPLETE")
        except:
            log(self.port, "SYNC FAILED")            # If for some reason the sync failed, print error message

    # Function for monitoring if server is main or not
    def monitor_leader(self):
        while True:
            self.is_main = (find_main() == (self.host, self.port))
            log(self.port, f"PRIMARY STATUS = {self.is_main}")
            time.sleep(2)

    # Function for handling incoming data
    # Input: connection (client or server)
    def handle(self, conn):
        data = conn.recv(100000).decode()                       # Decode data from TCP connection

        # Confirm if server is alive
        if data.startswith("PING"):
            conn.send(b"PONG")                                  # Respond to sender server with PONG

        # Send copy of file system to replica
        elif data.startswith("SYNC"):
            conn.send(json.dumps(self.fs).encode())             # Convert dictionary to JSON object first, because Python objects cannot be transmitted over TCP

        # Read operation
        elif data.startswith("READ"):
            _, path = data.split()                              # Separate read command from file path
            log(self.port, f"READ {path}")
            conn.send(self.read_file(path).encode())            # Send contents of requested file

        # Write operation
        elif data.startswith("WRITE"):
            # If server is not main, do not continue operation
            if not self.is_main:
                conn.send(b"ERROR")
                return

            # Write file
            _, path, content = data.split("\n", 2)              # Split write command, file path, and file contents into separate variables
            self.write_file(path, content)
            log(self.port, f"WRITE {path}")

            # Replication
            log(self.port, f"REPLICATING {path}")
            msg = f"REPL_WRITE\n{path}\n{content}"              # Construct command for replicating write
            self.replicate(msg)                                 # Replicate file write to replicas

            conn.send(b"WRITE COMPLETED")                       # Confirm to client that write was successful

        # Replicate write operation
        elif data.startswith("REPL_WRITE"):
            _, path, content = data.split("\n", 2)              # Split write command, file path, and file contents into separate variables
            log(self.port, f"WRITE {path}")               
            self.write_file(path, content)

        elif data.startswith("DELETE"):
            # If server is not main, do not continue operation
            if not self.is_main:
                conn.send(b"ERROR")
                return

            # Delete file
            _, path = data.split()                              # Split delete command from file path                
            self.delete_file(path)
            log(self.port, f"DELETED {path}")    

            # Replication
            self.replicate(f"REPL_DELETE {path}")               # Replicate delete to replicas
            conn.send(b"DELETE COMPLETED")                      # Confirm to client that delete was successful

        elif data.startswith("REPL_DELETE"):
            _, path = data.split()                              # Split replicate delete command from file path
            log(self.port, f"DELETED {path}")
            self.delete_file(path)

        elif data.startswith("LIST"):       
            _, path = data.split(maxsplit=1)                    # Split list directory command from file path
            log(self.port, f"LIST {path}")  
            conn.send(self.list_dir(path).encode())             # Call list_dir function and send directory contents

        conn.close()                                            # Close TCP connection

    def run(self):
        # Call sync_from_main function. If caller is main server, does nothing.
        # If caller is replica, syncs main server file system to own
        self.sync_from_main()

        # Run the monitor_leader function in parallel with other processes in run(). Because it runs parallel, it does not block 
        # other processes, allowing the server to react to main server crash without being blocked by other processes
        threading.Thread(target=self.monitor_leader, daemon=True).start()

        # Run the replica_connector_loop function in parallel with other processes in run(). Because it runs parallel, it does not block 
        # other processes, allowing the server to connect with new replica servers without being blocked by other processes.
        threading.Thread(target=self.replica_connector_loop, daemon=True).start()

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)       # Create TCP socket
        s.bind((self.host, self.port))
        s.listen()                                                  # Prepare to receive requests from client and other servers

        while True:
            conn, _ = s.accept()

            # Run the handle function in parallel with othe r processes in run(). Because it runs parallel, it does not block 
            # other processes, allowing the server to handle requests without being blocked by other processes.
            threading.Thread(target=self.handle, args=(conn,), daemon=True).start()