import itertools
from sympy import symbols
from sympy.logic import SOPform
from sympy.logic.boolalg import Not
import json
import sympy
import collections

# Working code to CREATE A MAX BOOLEAN CIRCUIT

    # NUM_INPUT_TO_CONFRONT : set to 4 or 8 or 16 or 32 to obtain a max boolean circuit 
    # NAME_OUTPUT_CIRCUIT : set here the name of the output json file containing the circuit

# This peogrm can be called using :         python createCircuitExtended.py

# This is the workflow :
#   - Generate the truth table for the Max for 8 inputs
#   - Divide table based on true output rows (the ones with 1)
#   - Generate SOP logic expression from the truth table
#   - Create a circuit form SOP logic expression using 8 input bits
#   - Replicate multiple times to manage more of that kind of unit
#   - Generate the circuit using NUM_INPUT_TO_CONFRONT (from it, one half if for Alice and other for Bob)


# this method generates the Truth Table
def gen_truth_table():
    
    # Truth table with 8 bit (4 for side)
    table = []
    
    for i, j in itertools.product(range(16), range(16)):
        maxn = max(i, j)
        input_bits = list(map(int, f'{i:04b}{j:04b}'))
        output_bits = list(map(int, f'{maxn:04b}'))
        row = (input_bits, output_bits)
        table.append(row)
        
        # Print the truth table row on video
        print(f"{row}")

    return table

# Funzione per dividere la tabella in base ai valori veri degli output
# Method to divide truth table based on True output, so the 1
def split_table(truth_table, value):
    truth_list = []
    
    # The outputs are locaded in the second element of the tuple
    out_length = len(truth_table[0][1]) 

    for bit in range(out_length):
        truth_sect = []
        for entry in truth_table:
            if entry[1][bit] == value:
                    
                # The Inputs are locaded in the first element of the tuple
                truth_sect.append(entry[0])  

        truth_list.append(truth_sect)
    return truth_list


# Mthod to generate SOP logic expressions
def gen_values(sym_list, truth_list):
    for t in truth_list:
        yield SOPform(sym_list, t)


# Print on video the obtained logic expressions
# Save them in a list val_exprs 

def max_logic_expression():
     
    truth_table = gen_truth_table()


    # Input Symbols
    a1, a2, a3, a4, b1, b2, b3, b4 = symbols('a1 a2 a3 a4 b1 b2 b3 b4')

    # Split the table
    truth_list = split_table(truth_table, 1)

    # Genera le espressioni logiche per ciascun bit di output
    # generate logic expressions for each output bit
    # val_exprs contains them 
    val_exprs = list(gen_values([a1, a2, a3, a4, b1, b2, b3, b4], truth_list))

    # Print logic expressions
    for i, val in enumerate(val_exprs, 1):
        print(f"\nLogic expression c{i}: \n\n{val}\n")

    return val_exprs


# This big function generates the circuit 
def circuit_gen(expr, input_values, start_id):
    # list of gates
    gates = []
    # starting id to assign to the new gates
    gate_id = start_id
    # dict to covert symbols in numbers
    
    def add_gate(type, inputs):
        nonlocal gate_id
        
        for gate in gates:

            if collections.Counter(gate["in"]) == collections.Counter(inputs):
                return gate
        
        new_gate = {"id": gate_id, "type": type, "in": inputs}
        gates.append(new_gate)
        # Update the gate ID number for new gates
        gate_id += 1
        return new_gate
    
    def add_not_gate(expr, translation):
        inputs = [translation[expr.args[0]]]
        gate = add_gate("NOT", inputs)
        return gate

    def add_and_gate(inputs):
        gate = add_gate("AND", inputs)
        return gate
    
    def add_or_gate(inputs):
        gate = add_gate("OR", inputs)
        return gate

    # This is the first layer that gets applied to boolan logic expression
    def add_not_layer(expr, translation):

        out_list = []

        for arg in expr.args:

            term_list = []

            for term in arg.args:
                if isinstance(term, sympy.Symbol):
                    term_list.append(translation[term])
                if isinstance(term, Not):
                    gate = add_not_gate(term, translation)
                    term_list.append(gate["id"])

            out_list.append(term_list)
        
        return out_list

    def add_and_layer(out_list):

        for i in range(len(out_list)):
            while(len(out_list[i]) > 1):
                gate = add_and_gate([out_list[i][0], out_list[i][1]])
                del out_list[i][0]
                del out_list[i][0]
                out_list[i].insert(0, gate["id"])

    def add_or_layer(new_list):

        while(len(new_list) > 1):
            gate = add_or_gate([new_list[0], new_list[1]])
            del new_list[0]
            del new_list[0]
            new_list.insert(0, gate["id"])

    def form_to_list(expr, input_values, sym_list):
        # The not layer is the first that get applied on inputs
        # We need to take care ot the output of these gates to supply them in future boolean operation

        translation = {}
        # range goes drom 1 to 8 because the input bits are 8
        for i in range(8):
            translation[sym_list[i]] = input_values[i]
        
        out_list = add_not_layer(expr, translation)

        return out_list

    def main():

        a1, a2, a3, a4, b1, b2, b3, b4 = symbols('a1 a2 a3 a4 b1 b2 b3 b4')

        # This list contains : 
        #       each internal list of elements in AND
        #       each external list of elements in OR
        sym_list = [a1, a2, a3, a4, b1, b2, b3, b4]

        out_list = form_to_list(expr, input_values, sym_list)

        add_and_layer(out_list)

        new_list = []

        for e in out_list:
            new_list.append(e[0])

        add_or_layer(new_list)

        output = new_list[0]
        new_start_id = gate_id

        return output, new_start_id, gates
    
    return main()



# inputs_values : list of 8 values that indicates input wires
# start_id is the next value we want to use to generate a new gate id
# it starts from the first free
def create_block(input_values, start_id):

    # Obtain logic expressions on wich we need to work
    val_exprs = max_logic_expression()

    # es. input_values = 01011010 - > the first and fourth bit are used to create the first new gate 
    gates_1 = [{'id': start_id, 'type': 'OR', 'in': [input_values[0],input_values[4]]}]

    out_gate_1 = start_id

    start_id += 1
    
    out_gate_2, start_id, gates_2 = circuit_gen(val_exprs[1], input_values, start_id)

    out_gate_3, start_id, gates_3 = circuit_gen(val_exprs[2], input_values, start_id)

    out_gate_4, start_id, gates_4 = circuit_gen(val_exprs[3], input_values, start_id)
    

    # Output bits of the circuit
    out_bits = [out_gate_1, out_gate_2, out_gate_3, out_gate_4]
    final_id = start_id

    # Dictionary, each one is a port
    gate_res = gates_1 + gates_2 + gates_3 + gates_4
    
    return out_bits, final_id, gate_res


def main():

    # How many numbers from both party we need to compare ? Es. 8 numbers, 4 for Alice and 4 for Bob
    #NUM_INPUT_TO_CONFRONT = 4
    #NUM_INPUT_TO_CONFRONT = 8
    #NUM_INPUT_TO_CONFRONT = 16
    NUM_INPUT_TO_CONFRONT = 32
    
    #NAME_OUTPUT_CIRCUIT = "max_4_num"
    #NAME_OUTPUT_CIRCUIT = "max_8_num"
    #NAME_OUTPUT_CIRCUIT = "max_16_num"
    NAME_OUTPUT_CIRCUIT = "max_32_num"

    NUM_BITS = 4

    # I want to confront NUM_INPUT_TO_CONFRONT numbers, half for Alice and half for Bob
    # Each number is reapresented using and encoding of 4 bits

    # es. NUM_INPUT_TO_CONFRONT is set to 32 -> 128 input bits (64 for Alice to rapresent her 16 numbers, idem for Bob)
    bits = NUM_INPUT_TO_CONFRONT * 4

    # Check if the number of bit is power of two and >= 2
    if not ((bits & (bits-1) == 0) and bits >= 8):
        print(f"ERROR: {NUM_INPUT_TO_CONFRONT} needs to be a power of 2 && >= 2")
        return

    bit_array = [e for e in range(1,bits+1)]
    starting_array = bit_array

    # We give 8 bits in input, next free ID is 9
    
    start_id = bits + 1
    gates_arr = []


    # Iterate until last 4 bites
    while(len(bit_array) > 4):    
        
        # block_list will contain each 8 bit group of the input_bit list
        block_list = []
        aux_arr = []
        
        # Grouping by 8 
        for i in range(len(bit_array)):

            aux_arr.append(bit_array[i])
            if not (i+1)%8:
                block_list.append(aux_arr)
                aux_arr = []


        # out bits of blocks created
        # when an iteration ends, gets updated to the new input_bit list using bits of block created
        outlist = []
        
        # This section effectively creates the circuits blocks and
        # combines them
        for e in block_list:
            out, start_id, gates = create_block(e, start_id)
            print("out:" + str(out))
            outlist = outlist + out
            for gate in gates:
                gates_arr.append(gate)

        # The next layer input bits are the outpust bits of the previous layer
        bit_array = outlist

    half = len(starting_array)//2

    circuit = {
    "name": NAME_OUTPUT_CIRCUIT,
    "circuits": [
            {
                "id": str(NUM_INPUT_TO_CONFRONT) + " numbers 4-bit MAX",
                "alice": starting_array[0:half],
                "bob": starting_array[half:len(starting_array)],
                "out": bit_array,
                "gates": gates_arr
            }
        ]
    }

    # Create the circuit file json using the chosen name
    with open(NAME_OUTPUT_CIRCUIT+".json", 'w') as outfile:
        json.dump(circuit, outfile,indent=4)


if __name__ == "__main__":
    main()