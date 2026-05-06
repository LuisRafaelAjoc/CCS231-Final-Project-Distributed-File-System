import socket

# Hardcoded server addresses and ports
SERVERS = [
    ("127.0.0.1", 8001),
    ("127.0.0.1", 8002),
    ("127.0.0.1", 8003),
]

# Cache for read operation. Dictionary that stores {file_path: content}
cache = {}

def send(msg):
    for server in SERVERS:
        try:
            with socket.create_connection(server, timeout=2) as sock:       # Establish connection with server
                sock.sendall(msg.encode())                                  # Encode and send message
                return sock.recv(100000).decode()                           # Return server response
        except:
            continue
    return None                 # If server is down, return None


def write(path, content):

    res = send(f"WRITE\n{path}\n{content}")

    # If server is up, it will 
    if res:
        print(res)
    else:
        print('ERROR: Server unreachable')
    # print(res if res else "ERROR: No server available")

    # If file that was overwritten is in cache, delete to ensure correctness during read operations
    if path in cache:
        del cache[path]

def read(path):

    # Check first if file is in cache
    if path in cache:
        print(f"FILE IN CACHE: {cache[path]}")      # Print message to alert user that cache was used
        return

    # Fetch file from server
    res = send(f"READ {path}")

    # If server successfully send file
    if res and not res.startswith("ERROR"):
        cache[path] = res                           # Store file in cache for future read operations
        print(res)
    else:
        print('ERROR: Server unreachable')

def delete(path):

    res = send(f"DELETE {path}")
    
    # If server is up, it will confirm deletion
    if res:
        print(res)
    else:
        print('ERROR: Server unreachable')

    # If the deleted file is in cache, delete it from cache
    if path in cache:
        del cache[path]

def showcache():
    print(cache)

def list_dir(path="/"):

    res = send(f"LIST {path}")
    # print(res if res else "ERROR: No server available")
    # If server us up, it will send list of directories and files
    if res:
        print(res)
    else:
        print('ERROR: Server unreachable')


def main():
    while True:
        try:
            cmd = input("\nInput: ").strip()          # Remove trailing whitespaces

            if cmd.lower() == "exit":
                print("Program has ended.")
                break

            elif cmd.startswith("write"):
                _, path, content = cmd.split(maxsplit=2)        # Remove 'write' from the input
                write(path, content)

            elif cmd.startswith("read"):
                _, path = cmd.split()                           # Remove 'read' from the input
                read(path)

            elif cmd.startswith("delete"):
                _, path = cmd.split()                           # Remove 'delete' from the input
                delete(path)

            elif cmd == 'showcache':                            # Print contents of cache
                showcache()

            elif cmd.startswith("list"):
                # Unlike the other operations, the input could be either just 'list' or
                # 'list {directory}', so we use just one variable to avoid error
                parts = cmd.split()                             

                # If list operation specified directory, list the files in that directory
                if len(parts) > 1:
                    list_dir(path=parts[1])                     # Ignore the first element in array ('list'), input directory path to list_dir
                
                # Otherwise, list the directories and files in root
                else:
                    list_dir(path='/')

            else:
                print("Unknown command. Accepted commands: write/read/delete/list/exit")
                
        except Exception as e:
            print("Error:", e)

main()