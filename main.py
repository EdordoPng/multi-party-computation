import logging
from alice import Alice
from bob import Bob


# This program needs to be executed from 2 party on the same machine.
# To do this :
#       1 ) Run Bob side.       Use : "python ./main.py bob"

#       2 ) Run Alice side.     To do this you can choose to use one of the supplied circuit to do the max.

#                                Use : "python ./main.py alice -c circuits/max_4_num.json"

#                             or Use : "python ./main.py alice -c circuits/max_8_num.json"

#                             or Use : "python ./main.py alice -c circuits/max_16_num.json"

#                             or Use : "python ./main.py alice -c circuits/max_32_num.json"     <------ Suggested 

# Based on which one you choose, you can compute :

#      max_4_num = 4 integer numbers in total (2 of Alice and 2 of Bob)
#      max_8_num = 8 integer numbers in total (4 of Alice and 4 of Bob)
#      max_16_num = 16 integer numbers in total (8 of Alice and 8 of Bob)
#      max_32_num = 32 integer numbers in total (16 of Alice and 16 of Bob)

def main(
    party,
    circuit_path="circuits/default.json",
    oblivious_transfer=True,
    print_mode="circuit",
    loglevel=logging.WARNING,
):
    logging.getLogger().setLevel(loglevel)

    if party == "alice":
        alice = Alice(circuit_path, oblivious_transfer=oblivious_transfer)

        # Method 1 

        alice.print_alice_to_bob()
        alice.write_alice_to_bob_to_json()
        
        # Method 2

        alice.start()
        # In ot.py : ObliviousTransfer.print_alice_ot() prints Alice side of the OT on alice_ot_side.txt
        # In ot.py : ObliviousTransfer.print_bob_ot() prints Bob side of the OT on bob_ot_side.txt

        # Method 3

        # In ot.py : ObliviousTransfer.bob_mpc_compute(self, reult) prints the output of the evaluation
        # In ot.py : Alice.alice_mpc_compute(...) prints the output the evaluation

        # Method 4
        
        # In bob.py : util.verfiy_output(bob_numbers_binary, bob_max_found_decimal, a_wires) calculates non MPC max anc compare it with the MPC one

    elif party == "bob":
        bob = Bob(oblivious_transfer=oblivious_transfer)
        bob.listen()
    else:
        logging.error(f"Unknown party '{party}'")


if __name__ == '__main__':
    import argparse

    def init():
        loglevels = {
            "debug": logging.DEBUG,
            "info": logging.INFO,
            "warning": logging.WARNING,
            "error": logging.ERROR,
            "critical": logging.CRITICAL
        }

        parser = argparse.ArgumentParser(description="Run Yao protocol.")
        parser.add_argument("party",
                            choices=["alice", "bob", "local"],
                            help="the yao party to run")
        parser.add_argument(
            "-c",
            "--circuit",
            metavar="circuit.json",
            default="circuits/max_16_num.json",
            help=("the JSON circuit file for alice and local tests"),
        )
        parser.add_argument("--no-oblivious-transfer",
                            action="store_true",
                            help="disable oblivious transfer")
        parser.add_argument(
            "-m",
            metavar="mode",
            choices=["circuit", "table"],
            default="circuit",
            help="the print mode for local tests (default 'circuit')")
        parser.add_argument("-l",
                            "--loglevel",
                            metavar="level",
                            choices=loglevels.keys(),
                            default="warning",
                            help="the log level (default 'warning')")

        main(
            party=parser.parse_args().party,
            circuit_path=parser.parse_args().circuit,
            oblivious_transfer=not parser.parse_args().no_oblivious_transfer,
            print_mode=parser.parse_args().m,
            loglevel=loglevels[parser.parse_args().loglevel],
        )

    init()
