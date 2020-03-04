# Multi-party trusted setup ceremony for Semaphore

This is where the Semaphore team we will keep track of the phase 2 trusted
setup.

The plan is to manually coordinate the ceremony while we complete a UI that
automates this process.

## How we will prepare for the ceremony

We will use [response
0022](https://github.com/weijiekoh/perpetualpowersoftau/tree/master/0022_roman_response)
from Perpetual Powers of Tau as the starting point.

We will apply a random beacon. We use the VDF Alliance's verifiable delay
function, with the [RSA-2048 modulus](https://en.wikipedia.org/wiki/RSA_numbers#RSA-2048). We will run the VDF for a duration of 600 minutes on an Ethereum block hash which we'll announce. We choose 600 minutes to be on the safe side - assuming an Ethereum block hash is considered to be somewhat final after 6 minutes, we could take a 6 minute VDF, if the VDF was optimal. While the current VDF service for 2048 bits already use an optimized implementation on an FPGA, it's still in progress, so we assume that a motivated attacker could develop a better one, with an extreme 100x advantage, so we run the VDF for 6\*100 minutes instead.

As such, we will choose the VDF output of the blockhash of block #____.

Finally, we will apply ___ rounds of the ___ hash
algorithm to the output and use the result as our random beacon.

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

TODO
