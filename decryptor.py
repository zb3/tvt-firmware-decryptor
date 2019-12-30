import sys
import struct
import binascii

from Crypto.Cipher import DES

# "public" key params - find them as strings in the UpgradeTool binary
exponent = 0x4F399773AEE1C039504734B592281FF1D33327EA8CB170AA963CB7AD38A20CC9
modulus  = 0x6E688026B4D604D6FC0E606F005A28A88EC5C24CAB101CEA85364C6B64CB5333

# of course the "private" exponent here is 0x10001 just as you'd expect
# apparently RSA is too hard for TVT to get right :D

def swap(buff, nbytes=8):
  return b''.join(buff[idx:idx+nbytes][::-1] for idx in range(0, len(buff), nbytes))

def decrypt_rsa32(data):
  db = int.from_bytes(swap(data, 4), 'big')
  return pow(db, exponent, modulus).to_bytes(32, 'big')

def decrypt_des(cipher, chunk):
  return swap(cipher.decrypt(swap(chunk)))

def read_encryption_info(file):
  # we'll read DES encryption info @0xb94, encrypted with RSA

  file.seek(0xb94)
  encrypted_einfo = file.read(0x40)

  # the first 4 bytes decrypted by RSA are 0
  # actually maybe decrypt_rsa32 produces swapped data, but we can just unpack it as BE

  einfo = decrypt_rsa32(encrypted_einfo[:32])[4:] + decrypt_rsa32(encrypted_einfo[32:])[4:]

  # now, the einfo is 56 bytes long, first 8 are the DES key
  des_key = einfo[:8]
  print('DES key:', des_key.hex())

  # then we have 10 offsets of encrypted 0x280 block chunks, but those offsets don't include the 0x1000 byte header
  encrypted_chunk_offsets = []
  encrypted_chunk_size = 0x280 << 3

  # those offsets don't include the 0x1000 byte header

  for x in range(10):
    offset = int.from_bytes(einfo[x*4+8:x*4+12], 'big') + 0x1000
    encrypted_chunk_offsets.append(offset)

    print('Encrypted chunk at', hex(offset))

  # what are the last 8 bytes for? I have no idea, maybe this is another checksum
  # but I didn't see these bytes used

  return des_key, encrypted_chunk_offsets, encrypted_chunk_size

def decrypt(input_path, output_path):
  with open(input_path, 'rb') as file:
    if file.read(0x10) != b'\xA7\x99\x27\x34\x3C\xA5\xAE\x49\x89\x3C\x88\xEB\x9B\x6A\xFE\x23':
      raise Exception('Unrecognized file format!')

    des_key, encrypted_chunk_offsets, encrypted_chunk_size = read_encryption_info(file)

    cipher = DES.new(des_key, DES.MODE_ECB)

    file.seek(0)

    with open(output_path, 'wb') as target:
      # copy file magic (should this be 0x10?)
      target.write(file.read(0x20))

      # now decrypt the header
      header = decrypt_des(cipher, file.read(0xb70))
      target.write(header)

      # then we have some unencrypted part, first 4 bytes are copied
      target.write(file.read(4))

      # the rest is discarded, zeros are written
      file.seek(0x1000)
      target.write(b'\x00' * (file.tell()-target.tell()))

      # then decrypt the data
      for offset in encrypted_chunk_offsets:
        if file.tell() < offset:
          target.write(file.read(offset - file.tell()))

        target.write(decrypt_des(cipher, file.read(encrypted_chunk_size)))

      # and copy the rest (actually nothing)
      target.write(file.read())


if __name__ == '__main__':
  if len(sys.argv) < 2:
    exit('No input file given')

  input_path = sys.argv[1]
  output_path = sys.argv[2] if len(sys.argv) >2 else input_path+'.raw'

  decrypt(input_path, output_path)
  print('Decryption complete, decrypted file written to '+output_path)
