#!/usr/bin/python3

###########################################################################
#  Copyright 2019 Supranational LLC
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
###########################################################################

import hashlib
import random
import sympy
import json

# Size of the small prime
PRIME_BITS = 256
PRIME_BYTES = PRIME_BITS // 8

# proof.json contains a proof of the below format. The values are examples:

#proof = {
#  # RSA challenge modulus
#  "modulus": "25195908475657893494027183240048398571429282126204032027777137836043662020707595556264018525880784406918290641249515082189298559149176184502808489120072844992687392807287776735971418347270261896375014971824691165077613379859095700097330459748808428401797429100642458691817195118746121515172654632282216869987549182422433637259085141865462043576798423387184774447920739934236584823824281198163815010674810451660377306056201619676256133844143603833904414952634432190114657544454178424020924616515723350778707749817125772467962926386356373289912154831438167899885040445364023527381951378636564391212010397122822120720357",
#
#  # Number of iterated squares
#  "t": "400000000000",
#
#  # Small prime
#  "l": "32764700963070804653119739479639726067136284033911258884251795331102117159421",
#
#  # Proof value
#  "pi": "4550490853460321083129782628907539706889083544969920676826398609077520014370191262656414289056435128601423558349640587013427217106254238434863313185697674511048467246569172676653633156130500878424186384755776039087394688318702752118180926419548900829891577420959903332715051295831370640288846295365959429189046197508176148488282866056367244643919187927397014668933154298001685549478958676686717782260293369552775413565378806277985034715079139224972409992422939081984935444803241512812661179425813722652474153642641848896683213950137825914896324789088157085624330473266770212861402943914910192579988927569432817172721",
#
#  # R, from paper
#  "r": "14619773157443873696967027589589807916607360999505076947551455227994206735341",
#
#  # VDF input value (i.e., Eth block hash). Must be equal to block_hash
#  "g": "11440827028973980734839007730550907915780281832104850997958208328182874869830",
#
#  # Final VDF evaluation value
#  "y": "7196895179844193832301373920786987284176235281849907738220764879371738189265496388165267942756374542747572449290932445084540043843509937179579762843862205226955928002040839868457390455888148544581618847026071090784498826663721271371453785594728901249648103823015220254754241557802074011117088397233532433747722657970522123129717614820592980331596619282803031421049894264255232669057824852427305348909009914693212848262566142217219318509427881134706746480740037287666672672120735495439543975100634661719283919043150373265215610734135600581763562809623870747249739600713807339974277385703302676795701466148328472033417",
#
#}

proof = json.loads(open('proof.json').read())
block_hash = int(proof['g'])

# Sample a prime
#  g - VDF input
#  y - VDF output
def sample_prime(g, y, desired_bits):
  append = 0
  l = None

  base_bytes = "{:x}*{:x}".format(g, y).encode()

  while True:
    l_in = base_bytes + append.to_bytes(PRIME_BYTES, byteorder='big')
    hash = hashlib.sha256(l_in).digest()
    l = int.from_bytes(hash, byteorder='big')
    
    mask = (1 << desired_bits) - 1
    l = l & mask
  
    if sympy.isprime(l):
      break

    # Number is not prime, increment and try again.
    append += 1

  return(l)

def check_in_group(e):
    return not e > modulus//2

def cast_to_group(e):
    if e > modulus//2:
        return modulus - e
    else:
        return e


modulus = int(proof['modulus'])

# Sample a prime
l = sample_prime(block_hash, int(proof['y']), PRIME_BITS)

# Verify proof
errors = 0
g = block_hash
if int(proof['l']) != l:
  print("ERROR: l does not match")
  errors += 1
  l = int(proof['l'])
    
t = int(proof['t'])
r = int(proof['r'])
y = int(proof['y'])
pi = int(proof['pi'])

if not check_in_group(g):
  print("ERROR: input is not in the quotient group")
  errors += 1

if not check_in_group(y):
  print("ERROR: output is not in the quotient group")
  errors += 1

if not check_in_group(pi):
  print("ERROR: proof is not in the quotient group")
  errors += 1
 
if cast_to_group(pow(2, t, l)) != r:
  print("ERROR: r does not match")
  errors += 1

if cast_to_group(pow(pi, l, modulus) * pow(g, r, modulus) % modulus) != y:
  print("ERROR: output does not match")
  errors += 1

if errors == 0:
  print("PASS!")
