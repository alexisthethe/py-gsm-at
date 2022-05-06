import time
import serial
import argparse


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class CallTestFail(Exception):
    pass


class Phone:
    def __init__(self, devname, pin, baudrate=115200, timeout=5, dial_timeout=60):
        self.devname = devname
        self.baudrate = baudrate
        self.timeout = timeout
        self.pin = pin
        self.dial_timeout = dial_timeout
        self.com = None

    def init(self):
        success = self.create_connection()
        if not success:
            raise CallTestFail("Cannot create connection with {}".format(self.devname))
        success = self.check_connection()
        if not success:
            raise CallTestFail("Connection to GSM failed")
        success = self.do_pin()
        if not success:
            raise CallTestFail("PIN login failed. BE CAREFUL NOT TO BLOCK YOUR SIM !!!!")


    def disconnect(self):
        if self.com:
            self.com.close()

    def create_connection(self):
        print("create connection to device {} with baudrate {}".format(self.devname, self.baudrate))
        start_time = time.time()
        while time.time() - start_time < self.timeout:
            time.sleep(0.5)
            try:
                self.com = serial.Serial(self.devname, self.baudrate, timeout=self.timeout)
                print("device ready")
                return True
            except serial.serialutil.SerialException:
                print("wait for device ready...")
                pass
        print("ERROR device can't be ready !")
        return False


    def check_response(self, response, timeout=None, KO_response=None):
        if timeout is None:
            timeout = self.timeout
        start_time = time.time()
        while time.time() - start_time < timeout:
            time.sleep(0.5)
            message = self.com.read_all()
            if message:
                print(message)
            if response in message:
                return True
            elif KO_response and KO_response in message:
                return False
        return False

    def check_OK(self):
        return self.check_response("OK")

    def check_connection(self):
        print("check connection...")
        self.com.write("AT\r")
        success = self.check_OK()
        if not success:
            print("connection ERROR !")
        return success

    def check_pin(self):
        print("check pin...")
        self.com.write("AT+CPIN?\r")
        return self.check_OK()

    def do_pin(self):
        print("enter pin code...")
        if self.check_pin():
            return True
        elif self.pin:
            self.com.write("AT+CPIN={}\r".format(self.pin))
            return self.check_response("PB DONE") and self.check_pin()

    def do_call(self, number):
        self.com.write("ATD{};\r".format(number))
        return self.check_OK()

    def leave_audio_message(self):
        self.check_response("VOICE CALL: BEGIN", self.dial_timeout, "NO CARRIER")
        time.sleep(10)

    def do_hangout(self):
        self.com.write("AT+CHUP\r")
        return self.check_OK()

    def wait_for_call_end(self):
        self.check_response("VOICE CALL: END", self.dial_timeout)

    def test_call(self, number):
        self.do_hangout()
        success = self.do_call(number)
        if not success:
            raise CallTestFail
        time.sleep(10)
        self.do_hangout()
        print(bcolors.OKGREEN + "CALL TEST OK !" + bcolors.ENDC)


def parse_args():
    parser = argparse.ArgumentParser(description='Test call on GSM module')
    parser.add_argument('device', metavar='dev', type=str,
                        help='the device path (ex: /dev/ttyUSB4)')
    parser.add_argument('number', metavar='num', type=str,
                        help='the phone number to call (ex: +33612345678)')
    parser.add_argument('pin', metavar='pin', type=str, nargs='?',
                        help='the SIM PIN code (ex: 0000)')

    args = parser.parse_args()
    print(args)
    return args

def main():
    args = parse_args()
    phone = Phone(args.device, args.pin)
    try:
        phone.init()
        phone.test_call(args.number)
    finally:
        phone.disconnect()

if __name__ == "__main__":
    main()
