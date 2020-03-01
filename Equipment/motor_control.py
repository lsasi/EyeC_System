# 0403:faf0
import sys
import time
from thorpy.comm.discovery import discover_stages
import os
# from thorpy.thorpy.comm.discovery import discover_stages
# from thorpy.thorpy.message import *


def set_position(s, position):
    try:
        s.position = position
    except:
        pass


def get_position(s):

    return str(s.position) + '\n'


def print_results(results):
    '''
    print to the results to stdout if needed
    and return the constructed string
    '''
    # if 'REQUEST_URI' in os.environ:
    #     out_string = gen_web_results(results)
    # else:
    #     out_string = gen_cons_results(results)
    # if not g_silent_mode:
    sys.stdout.write(str(results))
    return results


def run(verbose=False):
    # print(loc[0])

    stages = list(discover_stages())
    # print(stages)
    s = stages[0]

    s.home()
    # s.print_state()
    loc = sys.argv[1:]

    if loc[0].lower() == 'sp':
        pos = s.position
        position = float(loc[1])
        if verbose:
            print(position)
        set_position(s, position)

        if position < 0:
            while not (position * 0.95 > pos > position * 1.05):
                time.sleep(0.5)
                pos = s.position
                if verbose:
                    print(pos)
        elif position > 0:
            while not (position * 0.95 < pos < position * 1.05):
                time.sleep(0.5)
                pos = s.position
                if verbose:
                    print(pos)
        elif position == 0:
            while not -0.005 < pos < 0.005:
                time.sleep(0.5)
                pos = s.position
                if verbose:
                    print(pos)
        return print_results(str(get_position(s)))

    elif loc[0].lower() == 'gp':
        return print_results(str(get_position(s)))
    # s._port.send_message(MGMSG_HW_STOP_UPDATEMSGS())


if __name__ == "__main__":
    run()
    # print("Lior")