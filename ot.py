
import hashlib
import pickle
import util
import yao

class ObliviousTransfer:

    def __init__(self, socket, enabled=True):
        # Initialize the ObliviousTransfer object with a socket for communication
        self.socket = socket
        self.enabled = enabled

    # this function is called in main.py in the Alice class print(self, entry) function
    def get_result(self, a_inputs, b_keys):
        """Send Alice's inputs and retrieve Bob's result of evaluation.

        Args:
            a_inputs: A dict mapping Alice's wires to (key, encr_bit) inputs.
            b_keys: A dict mapping each Bob's wire to a pair (key, encr_bit).

        Returns:
            The result of the yao circuit evaluation.
        """
        print("################## Alice and Bob new Pair computation ##################\n ")
        print("Yao Protocol started \n")
        print(f"Alice sends her input to Bob : {a_inputs}\n")
        
        
        # Send the pair made from the key and encrypted bit to Bob
        # Remember that this entypted bit is the external value, i.e. that bit 
        # which will allow you to direct Bob to which row of the garbled table to decrypt 
        # Basically he is sending him ka0 or ka1 || it's at
        self.socket.send(a_inputs)

        for _ in range(len(b_keys)):
            
            # Alice receives da Bob il gate ID where to perform OT
            w = self.socket.receive()  

            print(f"Bob request a key for his input on the wire ID : {w} \n")

            if self.enabled:  
                
                pair = (pickle.dumps(b_keys[w][0]), pickle.dumps(b_keys[w][1]))
                print(f"Pair of keys Alice sends to the OT : {pair}")

                # Custom function to save on file also keys that Alice sends for each gate OT
                self.print_key_input_ot(pair, w)

                # With this the OT begins and ends, Bob has obtained mb
                self.ot_garbler(pair)
            else:
                print("Error here!")

        # Attende di ricevere il risultato della valutazione del circuito
        # da Bob tramite il socket 
        # Restituisce il risultato ricevuto, che è quello che Bob ottiene
        # dalla funzione send_result(...)

        # Waits to receive the circuit evaluation result from Bob via the socket 
        # Returns the received result, which is what Bob gets from the send_result(...) function
        return self.socket.receive()
    
    def print_key_input_ot(self, pair, gate):
        '''
            Method to print on file the keypair that Alice sends to Bob for each OT
        '''
        with open('alice_ot_side.txt', 'a') as file:
            
            file.write(f"Bob request an ot for the gate {gate} \n")
            file.write(f"Alice sends this pair of key to the OT\n{pair}\n\n")
        
    def bob_mpc_compute(self, result):
        '''
          Method to print Bob evaluation result
    
        '''
        bob_full_output = ""
        for key, value in result.items():
            bob_full_output += str(value)
  
        print(f"Bob full output {result}")

        bob_output_decimal = int(bob_full_output, 2)
        print(f"Bob output in decimal : {bob_output_decimal}")

        with open('bob_ot_side.txt', 'a') as file:
            
            file.write(f"Bob obtained with the MPC his result : {result}\n")
            file.write(f"In decimal : {bob_output_decimal} \n")
            file.write(f"\n################## Bob and Alice Pair Computation Ended ##################\n\n")

        return bob_output_decimal

    def send_result(self, circuit, g_tables, pbits_out, b_inputs):
        """Evaluate circuit and send the result to Alice.

        Called in bob.py in send_evaluation(self, entry)


        Args:Fo
            circuit: A dict containing circuit spec.
            g_tables: Garbled tables of yao circuit.
            pbits_out: p-bits of outputs.
            b_inputs: A dict mapping Bob's wires to (clear) input bits.
        """
        # map from Alice's wires to (key, encr_bit) inputs (Alice sent them at line 31)
        a_inputs = self.socket.receive()

        print(f"\nBob receives encrypted Alices input :\n {a_inputs}\n")
        
        # map from Bob's wires to (key, encr_bit) inputs
        # Dictionary that will hold the various mb obtained by Bob for his wires
        b_inputs_encr = {}
        
        print("Iterate for each wire :\n")
        for w, b_input in b_inputs.items():

            # For each gate Bob must choose whether to use the hb or hb-1 key
            print(f"Gate ID {w} ")
            print(f"Bob sends b = {b_input} to Alice to obtain the associed key for this gate")

            self.socket.send(w)

            if self.enabled:
                
                # Bob calls ot_evaluator to obtain from it the key||e (so mb)
                b_inputs_encr[w] = pickle.loads(self.ot_evaluator(b_input))
            else:
                print("Problema here ")
        
        print("\nBob done all the necessary OT \nBob starts circuit evaluation")

        # Bob evaluates the circuit 
        result = yao.evaluate(circuit, g_tables, pbits_out, a_inputs,
                              b_inputs_encr)
        # Call to print bob computation and obtain the converted in decimal result
        bob_output_decimal = self.bob_mpc_compute(result)

        print("\n################## Alice and Bob Pair Computation Ended ##################\n")
        
        # Bob circuit evaluation sent to Alice
        self.socket.send(result)

        return bob_output_decimal


    def print_alice_ot(self, data):
        '''
            Method to print the OT communication from the Alice's prospective
        '''
        # Note : here we are using the "append mode"
        with open('alice_ot_side.txt', 'a') as file:

            file.write(f"-------------- Alice starts the OT protocol\n")
            file.write(f"Send to Bob the Prime Group \n")
            file.write(f"Send to Bob c: {data['c']}\n")
            file.write(f"Send to Bob \nc1: {data['c1']}\n")
            file.write(f"e0: {data['e0']}\n")
            file.write(f"e1: {data['e1']}\n")
            file.write("-------------- Alice ends OT protocol\n\n")  # Aggiunge una riga vuota per separare i dati


    def ot_garbler(self, msgs):
        """
        Oblivious transfer, Alice's side.
        Called in alice.py in get_result

        Args:
            msgs: A pair (msg1, msg2) to suggest to Bob.
        """
        print("\n-------------------- Alice starts the OT protocol")
        # A group G of prime numbers is created and will be used in the protocol.
        G = util.PrimeGroup()
        
        # Alice sends it to Bob and waits for a confirmation response
        self.socket.send_wait(G)
        # OT protocol based on "Cryptography Made Simple" by Nigel Smart
        # We compute c = g^random_num
        c = G.gen_pow(G.rand_int())
        
        # We know that Bob will compute hb= g^x and also h1-b = c/hb  
        # Sending c and Receiving h0: c is sent to Bob, and Alice receives h0 in response.
        h0 = self.socket.send_wait(c)
        print(f"Alice manda c = {c} a Bob e ottiene indietro h0 = {h0}")

        # having obtained the value of h0 from Bob, Alice computes h1 = c/h0        
        h1 = G.mul(c, G.inv(h0))
        # Alice choose a random number and use it as secret key k 
        k = G.rand_int()
        # Compute c1 = g^k
        c1 = G.gen_pow(k)
        # Compute : m0 XOR H(h0^k)
        e0 = util.xor_bytes(msgs[0], self.ot_hash(G.pow(h0, k), len(msgs[0])))
        # Compute : m1 XOR H(h1^k)
        e1 = util.xor_bytes(msgs[1], self.ot_hash(G.pow(h1, k), len(msgs[1])))
        # Send these 3 to Bob
        self.socket.send((c1, e0, e1))
        
        
        print(f"Alice manda a Bob : \nc1 = {c1} \ne0 = {e0}  \ne1 = {e1}")

        data_to_write = {
            "c": c,
            "c1": c1,
            "e0": e0,
            "e1": e1
        }
        # Write OT protocols data from the Alice prospective
        self.print_alice_ot(data_to_write)

        print("-------------------- Alice ends OT protocol \n")

    def print_bob_ot(self, data):
        '''
            Method to print the OT communication from the Bob's prospective
        '''
        with open('bob_ot_side.txt', 'a') as file:
            
            file.write(f"-------------- Bob starts OT\n")
            file.write(f"Bob sends to OT his choice b = {data['b']}\n")
            file.write(f"Bob got from Alice c = {data['c']}\n")
            file.write(f"Bob got from Alice : \n")
            file.write(f"c1 : {data['c1']}\n")
            file.write(f"e0 : {data['e0']}\n")
            file.write(f"e1 : {data['e1']}\n")
            file.write(f"His key from the OT : mb = {data['mb']}\n")
            file.write(f"-------------- Bob Ends OT\n")
            file.write("\n") 

   

    def ot_evaluator(self, b):
        """Oblivious transfer, Bob's side.

        Args:
            b: Bob's input bit used to select one of Alice's messages.

        Returns:
            The message selected by Bob.
        """

        print("\n-------------------- Bob starts the OT protocol ")

        # Bob recieves the prime abelian group from Alice, it is public so non problem
        # Abelian means that a * b = b * a
        G = self.socket.receive()
        self.socket.send(True)

        # Alice chose a random c and sent it, here Bob receives it
        c = self.socket.receive()

        print(f"Bob got from Alice c = {c}")
        
        x = G.rand_int()
        x_pow = G.gen_pow(x)
        
        h = (x_pow, G.mul(c, G.inv(x_pow)))
        
        # Bob sends Alice the two pk values ​​hb and h1-b  
        # Bob doesn't need to send them both as Alice, having the c that 
        # originally sent to Bob, can get h1 from h0

        # Alice now encrypts m0 with h0 and m1 with h1
        # to do this it needs k0 and k1 random int which however 
        # they remain private and therefore Alice keeps them
        
        # Once this is done you will have obtained e0 and e1, i.e. two ciphertexts
        # In reality I have that k = k0 = k1, in fact you only need to use one
        # With story k Alice commutes c1 = g^k
        c1, e0, e1 = self.socket.send_wait(h[b])
        print(f"Bob got from Alice \n c1 = {c1} \n e0 = {e0} \n e1 = {e1}")

        # Create the pair of these two ciphertexts that Bob received
        # Pair of ciphertext that Bob got
        e = (e0, e1)
        # We need an Hash function H : G -> Bitstring of length n 
        ot_hash = self.ot_hash(G.pow(c1, x), len(e[b]))

        # mb = eb XOR H(c1^x)
        
        mb = util.xor_bytes(e[b], ot_hash)

        print(f"\n Bob got this key from the OT : {mb}")
        print("-------------------- Bob Ends the OT protocol \n")

        data_to_write = {
            "b": b,
            "c": c,
            "c1": c1,
            "e0": e0,
            "e1": e1,
            "mb": mb,
        }

        # Call to print whese informations on file
        self.print_bob_ot(data_to_write)

        return mb

    @staticmethod
    def ot_hash(pub_key, msg_length):
        """Hash function for OT keys."""
        key_length = (pub_key.bit_length() + 7) // 8  # key length in bytes
        bytes = pub_key.to_bytes(key_length, byteorder="big")
        return hashlib.shake_256(bytes).digest(msg_length)
