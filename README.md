# py-gsm-at
Python GSM AT commands call test

## Download the project

```
git clone git@github.com:alexisthethe/py-gsm-at.git
```

## Requirements

* Python
*  pip dependencies:
```
pip install -r requirements.txt
```

## Help

Get usage explanation :
```
python call_test.py -h
```

## Usage:

```
iusage: call_test.py [-h] dev num [pin]

Test call on GSM module

positional arguments:
  dev         the device path (ex: /dev/ttyUSB4)
  num         the phone number to call (ex: +33612345678)
  pin         the SIM PIN code (ex: 0000)

optional arguments:
  -h, --help  show this help message and exit
```

