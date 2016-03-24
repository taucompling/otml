import os
import platform
import sys

if platform.node() == "Iddos-MacBook-Pro.local":
    LOG_FOLDER = "/Users/iddoberger/Documents/MercurialRepositories/otml/source/logging"
else:
    LOG_FOLDER = "/home/idoberg1/loggingotml"

os.chdir(LOG_FOLDER)

simulation_name = "td_kg_aiu_aspiration_and_lengthening"


desired_grammar_line = 13
parse_line = 9
constraint_set_line = 6

def get_tail(log_name):
    print(log_name)
    block_lines = os.popen('tail -n 17 {}'.format(log_name)).read().split("\n")
    if "-->" not in block_lines[9]:
        print("no parse")
    else:
        for line in block_lines:
            print(line)

def find_log_files():
    find_pattern = 'find * -name "*{}*"'.format(simulation_name)
    log_names = os.popen(find_pattern).read().split()
    for log_name in log_names:
        get_tail(log_name)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        simulation_name = sys.argv[1]
    find_log_files()