import ot
import util


class Bob:
    """Bob is the receiver and evaluator of the Yao circuit.

    Bob receives the Yao circuit from Alice, computes the results and sends
    them back.

    Args:
        oblivious_transfer: Optional; enable the Oblivious Transfer protocol
            (True by default).
    """
    def __init__(self, oblivious_transfer=True):

        self.socket = util.EvaluatorSocket()
        # I create the Oblivious Transfer object by giving it the newly created socket
        # Here too the OT is activated by default
        self.ot = ot.ObliviousTransfer(self.socket, enabled=oblivious_transfer)


    
    def get_bob_inputs(self, out_wires, b_wires) :
        ''' Method to get Bob inputs from the Bob.txt file
            Process them to convert in binary 4-bit format 
            Check and discard invalid values
            Add 0 number to satisfy circuit input nuber request 
        '''
        with open("Bob.txt", 'r') as file:
            line = file.readline().strip()
            bob_dec_int = [int(num) for num in line.split()]


        valid_decimals = [num for num in bob_dec_int if num <= 15]
        interi_rimossi = [num for num in bob_dec_int if num > 15]

        # Print removed numbers
        for removed_int in interi_rimossi:
            print(f"Removed {removed_int} from the Bob input decimal numbers because not representable in 4-bit encoding")
    
        
        # If the inputs are too few respect how much we can use
        # we append 0 to complete the input number set
        if len(valid_decimals) < len(b_wires)/4:
            
            while len(valid_decimals) < len(b_wires)/4:
                valid_decimals.append(0)
        
        print(f"You can use us up to {len(b_wires)/4} decimal inputs in Bob.txt file")

        # If there are more integers respect how much we can deal with
        # just discard others when reached the cap
        if len(valid_decimals) > len(b_wires)/4:
            print("Too much decimal inputs in Bob.txt file")
            valid_decimals=valid_decimals[:len(b_wires)/4]

        
        # Use the number of ot wires to use that number of bit the number has  
        lunghezza = len(out_wires)
        bob_inputs_binary = [format(num, '0' + str(lunghezza) + 'b') for num in valid_decimals]

        print(f"\n\n\n\n Bob binary input : {bob_inputs_binary} \n\n\n\n")
        
        return bob_inputs_binary
            

    def listen(self):
        """Start listening for Alice messages."""

        print("Bob started listening")
        
        try:
            for entry in self.socket.poll_socket():
                # Confirm that Bob received the message
                self.socket.send(True)
                
                # Use the dict entry to start the computation
                self.send_evaluation(entry)

        except KeyboardInterrupt:
            print("Bob Stop Listening")

    # The dictionary entry contains all the information regarding:
    #   The circuit 
    #       From it I also get the list of wires for Alice and Bob
    #   I have some parity bit for each output
    #   The various garbled tables
    def send_evaluation(self, entry):
        """Evaluate yao circuit for all Bob and Alice's inputs and
        send back the results.

        Args:
            entry: A dict representing the circuit to evaluate.
        """
     
        circuit, pbits_out = entry["circuit"], entry["pbits_out"]
        garbled_tables = entry["garbled_tables"]
        a_wires = circuit.get("alice", [])  # list of Alice's wires
        b_wires = circuit.get("bob", [])  # list of Bob's wires
        out_wires = circuit.get("out", [])  # list of Bob's wires

        print(f"Received {circuit['id']}")

        # Obtain a list of Bob binary inputs
        bob_numbers_binary = self.get_bob_inputs(out_wires, b_wires)

        b_8bit_input = ""

        for num in bob_numbers_binary:
            b_8bit_input += num

        b_bit_list = [int(bit) for bit in str(b_8bit_input)]


        # Create dict mapping each wire of Bob to Bob's input
        b_inputs_clear = {
            b_wires[i]: b_bit_list[i]
            for i in range(len(b_wires))
        }
            
        print(f"\nStart comunication with Alice\n")
        print(f"Bob input : {b_inputs_clear} = {b_8bit_input}")
            
        # Evaluate and send result to Alice
        bob_max_found__decimal = self.ot.send_result(circuit, garbled_tables, pbits_out, b_inputs_clear)

        # Print the max found
        print(bob_max_found__decimal)
        
        # Verify function
        comparison_result = util.verify_output(bob_numbers_binary, bob_max_found__decimal, a_wires)
        
        print(f"It is {comparison_result} that MPC and NOT MPC are equal.")

        

    