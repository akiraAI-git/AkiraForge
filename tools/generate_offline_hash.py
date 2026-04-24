import bcrypt
import sys

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python generate_offline_hash.py <password>")
        sys.exit(1)

    pw = sys.argv[1]
    hashed = bcrypt.hashpw(pw.encode(), bcrypt.gensalt())
    print(hashed.decode())
