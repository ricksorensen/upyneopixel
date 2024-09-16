import argparse
import datetime


def getdate(dstr="None"):
    rv = None
    if dstr is None:
        return rv
    ct = datetime.datetime.now()
    if "(" in dstr:
        rv = dstr
    elif dstr == "now":
        rv = f"({ct.year}, {ct.month}, {ct.day})"
    elif dstr == "christmas":
        rv = f"({ct.year}, 12, 24)"
    elif dstr == "hanukkah":
        rv = f"({ct.year}, 12, 11)"
    elif dstr == "val":
        rv = f"({ct.year}, 2, 14)"
    elif dstr == "stpat":
        rv = f"({ct.year}, 3, 17)"
    return rv


def domain(args):
    # import shutil

    parser = argparse.ArgumentParser(
        description="Build basic holiday pixel driver configuration file",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--outfile",
        "-o",
        dest="cfile",
        type=str,
        default="config.py",
        help="output file",
    )
    parser.add_argument(
        "--mcu",
        "-M",
        dest="mcu",
        type=str,
        default="esp32c3",
        choices=["xiaoc3", "rp2", "xiaos3", "tinys3", "samd21", "nrf"],
        help="type of mcu (xiaoc3, xiaos3, rp2)",
    )
    parser.add_argument(
        "--ip",
        dest="ip",
        type=str,
        default=None,
        help="ip address (None if no networking)",
    )
    parser.add_argument(
        "--length",
        dest="length",
        type=int,
        default=300,
        help="LED strip length in leds",
    )
    parser.add_argument(
        "--deepsleep",
        dest="dsleep",
        action="store_true",
        help="use deep sleep if available",
    )
    parser.add_argument(
        "--random",
        dest="randomratio",
        type=int,
        default=None,
        help="insert random pixels every 1/n (None)",
    )
    parser.add_argument(
        "--date",
        dest="dateuse",
        type=str,
        default=None,
        # choices=["now", "christmas", "hanukkah", "stpat", "val", "hal", "(yr,mon,day)"],
        help="Specify date to use from list",
    )
    r = parser.parse_args(args)
    print(r)
    print("writing")
    # shutil.copy2(f"config.{args[0]}.py", "config.py")
    with open(r.cfile, "w") as fc:
        fc.write(f'_IP_ADDR = "{"192.168.1.250" if r.ip is None else r.ip}"\n')
        fc.write("_LONG_DUR = 200\n")
        fc.write("_TWINK_DUR = 100\n")
        fc.write(f"_NUM_PIX = {r.length}\n")
        fc.write("_HAN_DUR = 100\n")
        lpin = 2
        tpin = 21
        if r.mcu == "rp2":
            lpin = 26
            tpin = 0
            r.ip = None  # force no network
        fc.write(f"_NEOPIN = {lpin}\n")
        fc.write(f"_USE_NETWORK = {False if r.ip is None else True}\n")
        fc.write("_WAIT_NO_CONNECT = 120\n")
        duse = None if r.ip is not None else getdate(r.dateuse)
        fc.write(f"_USE_DATE = {duse}\n")
        fc.write("_TEMP_CORRECT = 20\n")
        fc.write("_SWAPRGB = True\n")
        fc.write(f"_TEMP_PIN = {tpin}\n")
        fc.write(f"_DEEPSLEEP = {r.dsleep}\n")
        fc.write("_DSLEEP_START = 19.1\n")
        fc.write(f"_RANDOM_RATIO = {r.randomratio}\n")
    print("Done")


if __name__ == "__main__":
    import sys

    domain(sys.argv[1:])
