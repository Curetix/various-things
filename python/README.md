# Python Scripts

## [compress_images.py](./compress_images.py)

Compress all JPEG and PNG images in a specified folder, overwriting the originals.

Usage: `python compress.py [IMAGE_FOLDER]`

## [fitness_faker.py](./fitness_faker.py)

Generate datasource and datasets of fitness data for Google Fit. Useful for the German [AOK Bonus App](https://www.aok.de/pk/bonus-praemienprogramme/programme-tarife/).

Requires Google API credentials.

Usage: `python fitness_faker.py --help`

## [shift_redeemer.py](./shift_redeemer.py)

Redeem a [GearBox SHiFT](https://shift.gearboxsoftware.com/) code for all games and platforms automatically.

Usage: `python shift_redeemer.py -e [EMAIL] -p [PASSWORD] [CODE]`

## [torguard_proxy_generator.py](./torguard_proxy_generator.py)

Generate a list of TorGuard proxy servers (Socks and HTTPS) URIs, intended to be used with JDownloader2.

Usage: `python torguard_proxy_generator.py -u [USERNAME] -p [PASSWORD]`
