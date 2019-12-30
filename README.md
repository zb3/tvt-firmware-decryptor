# tvt-firmware-decryptor
This tool helps you decrypt and unpack new firmware upgrade files for TVT DVRs, versions `1.3.x` and `1.4.x`. Those files have the `fls` extension.

While this works for `1.4.2`, it might not work for newer versions (and I'd actually expect it not to work, since currently TVT is using RSA keys incorrectly, see notes)

## Required packages
If you want to unpack that firmware for some reason, you probably already have all the needed things, congrats! :)

But being more specific, to simply decrypt the file, you need Python 3 with `PyCrypto`.

To unpack the file, you also need:
* `git` to fetch `squashfs-tools`
* `gcc`, `make`, `patch`, `libxz` etc to build it
* `binwalk` to extract the squashfs file

## Let's go

```
git clone https://github.com/zb3/tvt-firmware-decryptor
cd tvt-firmware-decryptor
```
and simply
```
./unpack.sh FIRMWARE_FILE
```
or to only decrypt:
```
python3 decryptor.py FIRMWARE_FILE [OUTPUT_FILE]
```

## Notes about repackaging
This tool doesn't contain any repackaging logic, my aim was only to unpack the firmware. But analysing `decryptor.py` will of course help a bit.

At first glance it appears that the firmware is signed with a RSA key, but actually what's embedded in the binary is the private key, see `decryptor.py` for more info.

Besides, the file has a checksum somewhere, but I didn't analyse that. For this you'd need to analyse the `UpgradeTool` binary in the unpacked filesystem.

### Squashfs note
TVT replaced the XZ stream header magic with
```
E2 74 56 74 00 50 4B 47 B3 E3 00
```
and the XZ stream footer magic with
```
05 C5 00 74 56 74 5E
```
