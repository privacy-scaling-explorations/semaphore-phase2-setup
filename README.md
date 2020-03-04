# Multi-party trusted setup ceremony for Semaphore

This is where the Semaphore team we will keep track of the phase 2 trusted
setup.

The plan is to manually coordinate the ceremony while we complete a UI that
automates this process.

## Ceremony progress

| Participant ID | Identity | GPG key | Attestation |
|-|-|-|-|
| 0001 | Koh Wei Jie | [Keybase](https://keybase.io/contactkohweijie) | [0001_weijie_response](./0001_weijie_response/README.md) |

## How we will prepare for the ceremony

We will use [challenge
0023](https://github.com/weijiekoh/perpetualpowersoftau/tree/master/0022_roman_response)
from Perpetual Powers of Tau as the starting point.

We will apply a random beacon. We use the VDF Alliance's verifiable delay
function, with the [RSA-2048 modulus](https://en.wikipedia.org/wiki/RSA_numbers#RSA-2048). We will run the VDF for a duration of 600 minutes on an Ethereum block hash which we'll announce. We choose 600 minutes to be on the safe side - assuming an Ethereum block hash is considered to be somewhat final after 6 minutes, we could take a 6 minute VDF, if the VDF was optimal. While the current VDF service for 2048 bits already use an optimized implementation on an FPGA, it's still in progress, so we assume that a motivated attacker could develop a better one, with an extreme 100x advantage, so we run the VDF for 6\*100 minutes instead.

As such, we will choose the VDF output of the blockhash of block #____.

Finally, we will apply ____ rounds of the SHA256 hash
algorithm to the output and use the result as our random beacon. The
`phase2-bn254` software's `beacon_constrained` binary will do this for us.

- Using the `ppot_fix` branch of
  [phase2-bn254](https://github.com/kobigurk/phase2-bn254), we will modify
  the source code (as the random beacon is hardcoded), rebuild the
  binaries, and use `beacon_constrained` to produce a `response`.

- Also using `ppot_fix`, we will run the `prepare_phase2` binary to
  generate radix files up to `phase1radix2m16`.

Next, we will initialise the phase2 ceremony.

- Using the `master` branch of phase2-bn254, we will run the `phase2` `new` binary: 

```bash
cargo run --release --bin new circuit.json circom1.params
```

Each participant must run the following for the file `circom<n>.params`:

```bash
cargo run --release --bin contribute circom<n>.params circom<n+1>.params <random entropy>
```

After each participant, the coordinator must run:

```bash
cargo run --release --bin verify_contribution circuit.json circom<n>.params circom<n+1>.params
```

And send `circom<n+1>.params` to the next participant.

When the UI is ready, we will verify all contributions and start from the latest
`.params` file.

At the end of the ceremony, we will generate the proving and verifying keys:

```bash
cargo run --release --bin export_keys circom<final>.params verification_key.json pk.json

cargo run --release --bin copy_json proving_key.json pk.json transformed_pk.json

mv transformed_pk.json /path/to/semaphore/circuits/build/proving_key.json
```

Note that `proving_key.json` was produced by `snarkjs` before the ceremony, and
only serves as a reference for the copy_json binary.

Finally, we use Semaphore's `build_snarks.sh` script to generate `proving_key.bin`
and `verifier.sol`.

## Instructions for each participant

First, set up a Linux machine and install Rust and Cargo following instructions [here](https://www.rust-lang.org).

Download and compile the required source code:

```bash
git clone https://github.com/kobigurk/phase2-bn254.git --branch semaphore-setup && \
cd phase2-bn254/phase2 && \
cargo build --release
```

Next, get the `circuit<n>.params` file from the coordinator.

In the `phase2` directory, run:

```bash
cargo run --release --bin contribute circom<n>.params circom<n+1>.params <random entropy>
```

Send the `circom<n+1>.params` file to the coordinator.

## Test run

1. Cloned `phase2-bn254` and switched to the `ppot_fix` branch

2. Ran `b2sum -b challenge` on challenge 0023

```
14e4fe7759391f2c6988e7902abd6343cc27d25980883aec39a88d1e415610b225e0aa5ac1ec9f5a40b699894767ac75983e5ca5441ebbc6ca66a61d049c9112 *../roman/new_challenge
```

3. Ran `beacon_constrained` with `challenge` 0023 in the current working directory.

```
ubuntu@ppotcoordinatorsea:/mnt/disk0/beacon_test$ ../ppot_fix/phase2-bn254/powersoftau/target/release/beacon_constrained
Will contribute a random beacon to accumulator for 2^28 powers of tau
In total will generate up to 536870911 powers                        
0: 0000000000000000000a558a61ddc8ee4e488d647a747fe4dcc362fe2026c620  
1: 0659d0f689b355b876b46cb515fcbadf69506e66b069a85a737d6fcc9958ecce
...
1023: af25c73da6f0fa1de98b7d677026a57513056403260fd80cfe3f4b65c71bf3a0
Final result of beacon: bb8eef164289bf02058b42c4ca2ac72013deb099bc79067e5779c9f1728b1271
Done creating a beacon RNG
Calculating previous contribution hash...
Contributing on top of the hash:
        dfcaaa51 9ada2419 256d73b4 1d944815
        4ff1b687 5874d44c f4e18be8 e933966e
        08db79db 40878856 78138e60 d3c82a9a
        7d50735c 449af38a 76d9ac9c 81af7e2a
Computing and writing your contribution, this could take a while...
Done processing 2097151 powers of tau

```

<!--4. Ran `prepare_phase2`.-->
