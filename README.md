# Multi-party trusted setup ceremony for Semaphore

This is where the Semaphore team we will keep track of the phase 2 trusted
setup.

The plan is to manually coordinate the ceremony while we complete a UI that
automates this process.

## Ceremony progress

TODO
<!--| Participant ID | Identity | GPG key | Attestation |-->
<!--|-|-|-|-|-->
<!--| 0001 | Koh Wei Jie | [Keybase](https://keybase.io/contactkohweijie) | [0001_weijie_response](./0001_weijie_response/README.md) |-->

## How we will run the ceremony

### 1. The challenge file

We will use the following challenge file from the Perpetual Powers of Tau
ceremony as the starting point. The Blake2b hash of the challenge file is:

```
    ab45d9d9 de4a950d a97ae2b1 d20fb7c6 
    1b6d1098 6cb02d41 8a8be0c6 4e2c99d6 
    c000a914 c03d9ab2 71ee07c0 990a41fb 
    56971420 2c380711 d722350c c19a1152
```

Its URL is:

```
https://ppot.blob.core.windows.net/public/challenge_0025
```

Even if the next participant completes a contribution before the VDF is over,
we will stick to the above challenge file.

### 2. The block hash

We will use the hash of block
[9689500](https://etherscan.io/block/countdown/9689500) on the Ethereum
mainnet, which will be mined around March 17 2020, 21:40:06 GMT+0800.

### 3. The VDF

We will generate the random beacon. We use the VDF Alliance's verifiable delay
function, with the [RSA-2048
modulus](https://en.wikipedia.org/wiki/RSA_numbers#RSA-2048). We will run the
VDF for a duration of 6000 minutes on the above Ethereum block hash. We choose
6000 minutes to be on the safe side - assuming an Ethereum block hash is
considered to be somewhat final after 6 minutes, we could take a 6 minute VDF,
if the VDF was optimal. While the current VDF service for 2048 bits already use
an optimized implementation on an FPGA, it's still in progress, so we assume
that a motivated attacker could develop a better one, with an extreme 1000x
advantage, so we will run the VDF for `6 * 1000` minutes instead.

The block hash is:

```
(TBD)
```

The above block hash as a decimal is:

```
1234...
```

We will convert the above block hash to a decimal using this Python3 snippet:

```python3
print(int('0xabcd...', 16))
```

The decimal will be fed into the VDF using this snippet:

```
mpz_set_str(
    x_in,
    "1234...",
    16
);
```

We will collaborate with [Supranational](https://www.supranational.net/), a
member of the [VDF Alliance](https://www.vdfalliance.org/), to compute the VDF.
The output of the VDF (4044943820224 iterations, which takes roughly 6000
minutes) is:

```
(TBD)
```

They will provide [verify_proof.py](./verify_proof.py) to verify the VDF proof.
This follows the [proof of correctness by
Wesolowski](https://eprint.iacr.org/2018/623.pdf).


4. The final output

We will *not* apply iterated SHA256 hashes to the output of the VDF. 

We will only apply one SHA256 hash to the VDF output so that we can get a
32-byte value which the `beacon_constrained` program requires.


To convert the VDF output (e.g. the decimal 12345....), we will use the
following Python 3 code:

```python3
import hashlib

vdf_output = hex(12345....)

m = hashlib.sha256()
m.update(bytes.fromhex(vdf_output[2:]))
sha256_input = m.digest()

print(sha256_input.hex())
```

<!--We will run `2 ^ 42 = 4398046511104` rounds of the SHA256 hash algorithm to the-->
<!--SHA256 hash of the output and use the result as our random beacon. The SHA256-->
<!--hash of the VDF output is `(TBD)`, and we use-->
<!--[`verify-beacon`](https://github.com/kobigurk/verify-beacon) to perform the-->
<!--iterated hashes. The process will take about 58 hours using an AMD EPYC 7401P-->
<!--24-Core Processor @ 2.0GHz.-->

<!--The final hash is:-->

<!--```-->
<!--(TBD)-->
<!--```-->

<!--Anyone can use `verify-beacon` to quickly verify the final hash (as the-->
<!--`verify` program performs the checks in parallel).-->

<!--```bash-->
<!--./target/release/verify < ppot_output.txt-->
<!--```-->

While the Semaphore team will not use this output as the random beacon, we will
release it for other teams if they so choose to use it.

### 5. Applying the beacon

Using the `ppot_fix` branch of
[phase2-bn254](https://github.com/kobigurk/phase2-bn254) (commit hash
52a9479810f583c58156db292c0a3762ee790af7), we will modify the source code (as
the random beacon is hardcoded), rebuild the binaries, and use
`beacon_constrained` to produce a `response`.

Also using `ppot_fix`, we will run the `prepare_phase2` binary to generate
radix files up to `phase1radix2m16`.

Next, we will initialise the phase2 ceremony.

- Using the `master` branch of phase2-bn254 (commit hash 5d82e40bb7361d422ff6b68a733a14662a16aa05), we will run the `phase2` `new` binary: 

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
git clone https://github.com/kobigurk/phase2-bn254.git --branch ppot_fix && \
cd phase2-bn254/phase2 && \
cargo build --release
```

Next, get the `circuit<n>.params` file from the coordinator.

In the `phase2` directory, run:

```bash
cargo run --release --bin contribute circom<n>.params circom<n+1>.params <random entropy>
```

Send the `circom<n+1>.params` file to the coordinator.

Please also write an
attestation to your contribution and sign it with a GPG key, Keybase account,
or Ethereum account using the example
[here](https://github.com/weijiekoh/perpetualpowersoftau/blob/master/README.md#your-attestation).

## Logistics

To be confirmed: each participant needs to download a 22M `.params` file and
upload a 22M `.params` file. The computation time should take no more than a
minute on a modern laptop.

For convenience, we will use Dropbox to share the `.params` files. The
coordinator will back them up to Azure blob storage and IPFS.

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
...
Done processing 536870910 powers of tau
Finihsing writing your contribution to `./response`...
Done!

Your contribution has been written to `./response`

The BLAKE2b hash of `./response` is:
        52daebb5 4b113656 f7367e29 7d430394
        da749ab9 b6e195da 1d3499ea b63aeacc
        d4e0a252 9ab06ef0 be1c4eb6 d01b3442
        feb12c9d c0523a8c a2331d66 ffb561e8
Thank you for your participation, much appreciated! :)
```

4. Ran `prepare_phase2`.
