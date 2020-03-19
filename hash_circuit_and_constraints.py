#!/usr/bin/env python3

import sys
import json
import hashlib

def main():
    # The first argument should be the circuit.json file
    if len(sys.argv) == 0:
        print("Please specify the path to circuit.json")

    circuit_file = sys.argv[1]

    # load the constraints from circuit.json
    circuit = json.loads(open(circuit_file).read())
    constraints = circuit["constraints"]
    
    # hash the JSON encoding of the constraints
    hasher = hashlib.sha256()
    hasher.update(bytes(json.dumps(constraints).encode("utf-8")))
    result = hasher.digest().hex()

    print(result)

if __name__ == "__main__":
    main()
