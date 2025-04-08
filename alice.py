import ot
import util
import json
import base64
from yaoGarbler import YaoGarbler

class Alice(YaoGarbler):
    """Alice is the creator of the Yao circuit.

    Alice creates a Yao circuit and sends it to the evaluator along with her
    encrypted inputs. Alice will finally print the truth table of the circuit
    for all combination of Alice-Bob inputs.

    Alice does not know Bob's inputs but for the purpose
    of printing the truth table only, Alice assumes that Bob's inputs follow
    a specific order.

    Attributes:
        circuits: the JSON file containing circuits
        oblivious_transfer: Optional; enable the Oblivious Transfer protocol
            (True by default).
    """
    def __init__(self, circuits, oblivious_transfer=True):
        
        # Call the YaoGarbler base class constructor. 
        # Circuits is a string with the path to the json file
        super().__init__(circuits)

        # Once this is done I have that the self.circuits list will contain all the 
        # information that you will then have to send to Bob 
        # Initialize a socket for the garbler.
        self.socket = util.GarblerSocket()

        # Initialize an instance of the Oblivious Transfer protocol with the socket.
        self.ot = ot.ObliviousTransfer(self.socket, enabled=oblivious_transfer)

    # I	deleted the for cycle used to work with multiple circuits 
    # (in this project we work only with circuits/max_4_bit.json)
    def start(self):
        """ Alice start Yao protocol.
            
            Send preliminar informations to Bob
            
            Calls the print() method to go on with the execution"""
        # Take the first circuit obtained in the parent class YaoGarbler 
        # We need to work just with the 4-Bit max circuit
        circuit = self.circuits[0]
        
        # Informations that Alice sends to Bob so to do the computation with them
        to_send = {
            "circuit": circuit["circuit"],
            "garbled_tables": circuit["garbled_tables"],
            "pbits_out": circuit["pbits_out"],
        }

        # Alice sends these informations to Bob via socket
        self.socket.send_wait(to_send)

        self.print(circuit)

  
    def print(self, entry):
        """Print circuit evaluation for all Bob and Alice inputs.

        Args:
            entry: A dict representing the circuit to evaluate.
        """

        # Keys is a dictionary with a pair of keys for each wire
        # Alice already obtained keys, generated in the parent class
        circuit, pbits, keys = entry["circuit"], entry["pbits"], entry["keys"]
        outputs = circuit["out"]
        a_wires = circuit.get("alice", [])   
        # New dictionary to map from Alice's wires to (key, encr_bit) inputs
        a_inputs = {} 

        # Get Alice's imput from Alice.txt
        alice_numbers = self.get_ali_inputs()

        b_wires = circuit.get("bob", [])  
        # New dictionary to map from Bob's wires to a pair (key, encr_bit) 
        b_keys = { 
            w: self._get_encr_bits(pbits[w], key0, key1)
            for w, (key0, key1) in keys.items() if w in b_wires
        }

        print(f"======== {circuit['id']} ========")

        a_8bit_input = ""

        for num in alice_numbers:
            a_8bit_input += num
        
        bit_list = [int(bit) for bit in str(a_8bit_input)[:len(a_wires)]]

        # Scroll along all Alice's wires
        for i in range(len(a_wires)):

            # The second one calculates the encrypted bit (encr_bit) using an XOR operation 
            # In practice it would be ka0 or ka1 || ea
            # In the key dictionary I first select the wire and then which of the two keys to use
            a_inputs[a_wires[i]] = (keys[a_wires[i]][bit_list[i]],
                                    pbits[a_wires[i]] ^ bit_list[i])
            

        # This result is obtained by Bob computation
        result = self.ot.get_result(a_inputs, b_keys)

        # Format output
        str_bits_a = ' '.join(a_8bit_input[:len(a_wires)])
        str_result = ' '.join([str(result[w]) for w in outputs])


        self.alice_mpc_compute(result, a_wires, str_bits_a, b_wires, outputs, str_result)

        print(f"  Alice{a_wires} = {str_bits_a} "
              f"Bob{b_wires} = "
              f"Outputs{outputs} = {str_result}")
            
        print(f"\n################## Alice and Bob Computation Ended ##################\n")

    
    def alice_mpc_compute(self, result, a_wires, str_bits_a, b_wires, outputs, str_result):
        ''' Write alice output computed via MPC to the file

        Args:
            result : dictionary with assotiations key : value 
                     uses out gates ad key and the corrisponding bit computed as value
            a_wires : list of Alice's wires
            b_wires : list of Bob's wires
            outputs : list of output gates
            str_result : result of the computation 
        '''
        with open('alice_ot_side.txt', 'a') as file:
            # Write values in file
            file.write(f"Alice{a_wires} = {str_bits_a} "
                  f"Bob{b_wires} = ???  "
                  f"Outputs{outputs} = {str_result}\n")
            file.write(f"\nAlice obtained from Bob the result : {result}\n")
            file.write(f"\n################## Alice and Bob Pair Computation Ended ##################\n\n")

        
    def print_alice_to_bob(self):
        ''' Print on screen preliminar informations that Alice sends to Bob
        '''
        
        # Take the first circuit since I only use one, namely the max.json one
        circuit = self.circuits[0]

        to_send = {
                "circuit": circuit["circuit"],
                "garbled_tables": circuit["garbled_tables"],
                "pbits_out": circuit["pbits_out"],
        }
        rule_5 = { 
            "keys": circuit["keys"],
            "pbits": circuit["pbits"],
            "garbled_circuit": circuit["garbled_circuit"],
        }
        print("\nInformazioni che Alice manda a Bob :\n")
    
        # Alice sends the json circuit file
        print(f"1) Circuit : \n\n {to_send['circuit']} \n", )
        
        # Sends the garbled tables.
        # Commented becouse too big to print on screen 
        #print(f"2 ) Garbled tables : {to_send['garbled_tables']}\n", )
        print(f"2 ) Garbled tables : Not printed becouse too big, decomment to print on screen \n", )

        # Sends the parity bit of output gate
        print(f"3 ) Parity Bit of the output gate: {to_send['pbits_out']} \n", )

        print("\nInformations Alice send to Bob :\n")
        print(f"1 ) The keys of the circuit that Alice created are:\n {rule_5['keys']} \n", )
        print(f"2 ) Parity bit of keys :\n {rule_5['pbits']} \n", )
        print(f"3 ) Grabled Circuit:\n {rule_5['garbled_circuit']} \n", )
    
        print("End preliminar information transmission. \n")


    def write_alice_to_bob_to_json(self):
        '''Write on file the preliminar informations that Alice sends to Bob
        '''
        # Take the first circuit since I only use one, namely the max.json one
        circuit = self.circuits[0]
        garbled_tables = circuit["garbled_tables"]

        # Need to convert to write it on file
        garbled_tables_base64 = {
        str(key): {
           str(sub_key): base64.b64encode(value).decode('utf-8') for sub_key, value in sub_dict.items()
        } for key, sub_dict in garbled_tables.items()
        }

        to_send = {
            "circuit": circuit["circuit"],
            "garbled_tables": garbled_tables_base64,
            "pbits_out": circuit["pbits_out"],
        }
        keys = circuit["keys"]
        
        # Need to convert to write it on file
        keys_base64 = {
        key: {
            'value1': base64.b64encode(value[0]).decode('utf-8'),
            'value2': base64.b64encode(value[1]).decode('utf-8')
        } for key, value in keys.items()
        }
    
        # It is used to print the things requested in rule 5 of the delivery
        rule_5 = {
            "keys": keys_base64,
            "pbits": circuit["pbits"],
            # It is the Gabled Circuit object, so we don't write it
            #"garbled_circuit": circuit["garbled_circuit"],
        }

        data_to_write = {
        
            "to_send": to_send,
            "INFORMAZION ":"INFORMATION THAT ALICE KEEPS FOR HER",
            "rule_5": rule_5,
            "INFORMAZIONI PRELIMINARI DI ALICE - ":"TERMINATE"
        }

        # Write data in file JSON
        with open('output_alice_bob.json', 'w') as file:
            json.dump(data_to_write, file, indent=4)

        print("Preliminar informations wrote in 'output_alice_bob.json'\n")
        # Prende un singolo pbit e 2 chiavi

    def get_ali_inputs(self) :
        ''' Obtain Alice's inputs from Alice.txt 
            Process them to convert in binary 4-bit format 
            Check and discard invalid values
            Add 0 number to satisfy circuit input number request 
        '''

        cir = self.circuits[0]["circuit"]
        lista_wire_out = cir.get("out", [])
        lista_wire_ali = cir.get("alice", [])
        
        len_wire_out = len(lista_wire_out)
        
        with open("Alice.txt", 'r') as file:
            line = file.readline().strip()
            interi_decimali = [int(num) for num in line.split()]

        # Removing elements that cannot be represented in 4-bit encoding
        valid_decimals = [num for num in interi_decimali if num <= 15]
        interi_rimossi = [num for num in interi_decimali if num > 15]

        # Print removed numbers
        for removed_int in interi_rimossi:
            print(f"Removed {removed_int} from the input decimal numbers because not representable in 4-bit encoding")
    
        # If the inputs are too few respect how much we can use
        # we append 0 to complete the input number set
        if len(valid_decimals) < len(lista_wire_ali)/4:
            
            while len(valid_decimals) < len(lista_wire_ali)/4:
                valid_decimals.append(0)
        
        print(f"\nYou can give up to {int(len(lista_wire_ali)/4)} decimal inputs in Alice.txt file with the chosen circuit")

        # If there are more integers respect how much we can deal with
        # just discard others when reached the cap
        if len(valid_decimals) > len(lista_wire_ali)/4:
            print("Too much decimal inputs in Alice.txt file")
            valid_decimals=valid_decimals[:len(lista_wire_ali)/4]
        
        # Convert in binary rapreentation using 4-bit encoding
        ali_binary = [format(num, '0' + str(len_wire_out) + 'b') for num in valid_decimals]

        print(f"\n\n\n\n Alice binary input : {ali_binary} \n\n\n\n")
        
        return ali_binary


    def _get_encr_bits(self, pbit, key0, key1):
        
        return ((key0, 0 ^ pbit), (key1, 1 ^ pbit))
