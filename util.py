import json
import operator
import random
import secrets
import sympy
import zmq

# SOCKET
LOCAL_PORT = 4080
SERVER_HOST = "localhost"
SERVER_PORT = 4080


class Socket:
    def __init__(self, socket_type):
        self.socket = zmq.Context().socket(socket_type)
        self.poller = zmq.Poller()
        self.poller.register(self.socket, zmq.POLLIN)

    def send(self, msg):
        self.socket.send_pyobj(msg)

    def receive(self):
        return self.socket.recv_pyobj()

    def send_wait(self, msg):
        self.send(msg)
        return self.receive()

    """
    From https://stackoverflow.com/questions/17174001/stop-pyzmq-receiver-by-keyboardinterrupt
    """

    def poll_socket(self, timetick=100):
        try:
            while True:
                obj = dict(self.poller.poll(timetick))
                if self.socket in obj and obj[self.socket] == zmq.POLLIN:
                    yield self.socket.recv_pyobj()
        except KeyboardInterrupt:
            pass


class EvaluatorSocket(Socket):
    def __init__(self, endpoint=f"tcp://*:{LOCAL_PORT}"):
        super().__init__(zmq.REP)
        self.socket.bind(endpoint)


class GarblerSocket(Socket):
    def __init__(self, endpoint=f"tcp://{SERVER_HOST}:{SERVER_PORT}"):
        super().__init__(zmq.REQ)
        self.socket.connect(endpoint)


def verify_output(bob_numbers_binary, bob_max_found_decimal, a_wires):
    '''
    bob_numbers_binary : list of bob inputs in binary 4bit encoded form
    bob_max_found_decimal : max MPC result
    a_wires : list of Alice's input wires
    '''
    with open("Alice.txt", 'r') as file:
        line = file.readline().strip()
        interi_decimali = [int(num) for num in line.split()]

    # Remove elements that are not rapresentable using 4 bit encoding
    
    ali_decimals = [num for num in interi_decimali if num <= 15]
    
    valid_ali_decimals = []
    
    if len(ali_decimals) > len(a_wires)/4:
        print("Too much decimal inputs in Alice.txt file")
        valid_ali_decimals = ali_decimals[:len(a_wires)/4]
    else :
        valid_ali_decimals = ali_decimals

    # Convert the list of binary numbers in 4 bit encoding in a list of decimal numbers
    bob_valid_decimal = [int(binary_num, 2) for binary_num in bob_numbers_binary]
        
    bob_inputs = bob_valid_decimal

    union = valid_ali_decimals + bob_inputs
    maxx = max(union)

    print(f"Max values MPC : {bob_max_found_decimal}")
    print(f"Max values No MPC : {maxx}")
    

    if maxx == bob_max_found_decimal:
        print("Perfect, no errors")

        return True
    else:
        print(f"Errors") 
        return False




# PRIME GROUP
PRIME_BITS = 64  # order of magnitude of prime in base 2


def next_prime(num):
    """Return next prime after 'num' (skip 2)."""
    return 3 if num < 3 else sympy.nextprime(num)


def gen_prime(num_bits):
    """Return random prime of bit size 'num_bits'"""
    r = secrets.randbits(num_bits)
    return next_prime(r)


def xor_bytes(seq1, seq2):
    """XOR two byte sequence."""
    return bytes(map(operator.xor, seq1, seq2))


def bits(num, width):
    """Convert number into a list of bits."""
    return [int(k) for k in f'{num:0{width}b}']


class PrimeGroup:
    """Cyclic abelian group of prime order 'prime'."""
    def __init__(self, prime=None):
        self.prime = prime or gen_prime(num_bits=PRIME_BITS)
        self.prime_m1 = self.prime - 1
        self.prime_m2 = self.prime - 2
        self.generator = self.find_generator()

    def mul(self, num1, num2):
        "Multiply two elements." ""
        return (num1 * num2) % self.prime

    def pow(self, base, exponent):
        "Compute nth power of an element." ""
        return pow(base, exponent, self.prime)

    def gen_pow(self, exponent):  # generator exponentiation
        "Compute nth power of a generator." ""
        return pow(self.generator, exponent, self.prime)

    def inv(self, num):
        "Multiplicative inverse of an element." ""
        return pow(num, self.prime_m2, self.prime)

    def rand_int(self):  # random int in [1, prime-1]
        "Return an random int in [1, prime - 1]." ""
        return random.randint(1, self.prime_m1)

    def find_generator(self):  # find random generator for group
        """Find a random generator for the group."""
        factors = sympy.primefactors(self.prime_m1)

        while True:
            candidate = self.rand_int()
            for factor in factors:
                if 1 == self.pow(candidate, self.prime_m1 // factor):
                    break
            else:
                return candidate


# HELPER FUNCTIONS
def parse_json(json_path):
    with open(json_path) as json_file:
        return json.load(json_file)
