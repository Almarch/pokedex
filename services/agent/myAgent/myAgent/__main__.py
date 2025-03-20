import uvicorn
import sys

# Configuration
OLLAMA_URL = "http://ollama:11434"
LOG_DIR = "/logs"
QDRANT_HOST = "qdrant"
QDRANT_PORT = 6333
ENCODER = "snowflake-arctic-embed2:568m-l-fp16"

def main():
    host = "127.0.0.1"
    port = 8000

    if len(sys.argv) > 1:
        host = sys.argv[1]
    if len(sys.argv) > 2:
        try:
            port = int(sys.argv[2])
        except ValueError:
            print("Error: Port must be an integer.")
            sys.exit(1)

    uvicorn.run("myAgent.app:app", host=host, port=port, reload=False)

if __name__ == "__main__":
    main()
