from abc import ABC, abstractmethod
import util
import yao

class YaoGarbler(ABC):
    """An abstract class for Yao garblers (e.g. Alice)."""
    # The circuit that the constructor does is a json file that contains
    def __init__(self, circuits):
        
        
        circuits = util.parse_json(circuits)
        self.name = circuits["name"]
        # In my project I use just one, the 4-bit Max
        self.circuits = []
        
        for circuit in circuits["circuits"]:
            
            # Create an instance of GarbledCircuit for the current circuit using 
            # a function of the yao module
            garbled_circuit = yao.GarbledCircuit(circuit)
            # Get the p-bits (i.e. random bits associated with the circuit wires) from the garbled circuit.
            pbits = garbled_circuit.get_pbits()
            # Creation of entry for the circuit 
            entry = {
                "circuit": circuit,
                "garbled_circuit": garbled_circuit,
                "garbled_tables": garbled_circuit.get_garbled_tables(),
                "keys": garbled_circuit.get_keys(),
                "pbits": pbits,
                "pbits_out": {w: pbits[w] for w in circuit["out"]},
            }
            # Append to circuits
            self.circuits.append(entry)
    
    @abstractmethod
    def start(self):
        pass