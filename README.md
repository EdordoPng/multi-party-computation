# Multi-Party Computation

This project implements a secure **Multi-Party Computation (MPC)** protocol using **Yao's Garbled Circuits** to calculate the maximum value between two sets of integers provided by Alice and Bob.

## Garbled Circuits - Maximum of Two Sets of Values

This implementation demonstrates a secure **Multi-Party Computation (MPC)** protocol using **Yao's Garbled Circuits** to calculate the **maximum value** between two sets of integers provided by **Alice** and **Bob**.

### 🐍 Python Version

Tested with **Python 3.10.1**

### 🚀 Quickstart

#### 1. Install Dependencies

To install the required dependencies, you can run the following command:

```bash
pip install -r requirements.txt
```

Alternatively, use:

```bash
pip3 install --user pyzmq cryptography sympy
```

### 📦 Dependencies

The dependencies include:
* **pyzmq**: for the communication socket
* **cryptography**: for the operations crittografiche
* **sympy**: for the logica booleana and the generation of circuits
* **base64io**: for the serialization of data
* **json5**: for the management of file JSON
* **itertools**: for the generation of truth tables
* **collections**: for handling data structures


#### 2. Prepare Input Files

Modify the `inputs/Alice.txt` and `inputs/Bob.txt` files with decimal integers (0-15). Inputs outside this range will be ignored. Missing values will be padded with 0.

#### 3. Run the Protocol

Use two terminals:

**Terminal 1 – Bob**
```bash
python main.py bob
```

**Terminal 2 – Alice**
```bash
python main.py alice -c circuits/max_32_num.json
```

**Available Circuits:**
- `max_4_num.json` — 2 values per side
- `max_8_num.json` — 4 values per side
- `max_16_num.json` — 8 values per side
- `max_32_num.json` — 16 values per side

### 🛠️ Files Overview

- `main.py` — Entry point for Alice and Bob
- `alice.py`, `bob.py` — Role-specific logic
- `yaoGarbler.py`, `yao.py` — Core MPC logic
- `ot.py` — **Oblivious Transfer** logic
- `util.py` — Utility functions including verification
- `createCircuitExtended.py` — Tool to create new max circuits

#### 📄 Output Files

After execution, the following files are generated in the `outputs/` folder:
- `output_alice_bob.json`
- `alice_ot_side.txt`
- `bob_ot_side.txt`

These files contain:
- **Garbled circuit** and keys
- Inputs/outputs of OT from both sides
- Final result of the **maximum operation**

### 📡 Protocol Flow (Simplified)

**Alice:**
- Generates **garbled circuit** and keys
- Sends garbled tables and inputs
- Executes OT from her side
- Receives and verifies result

**Bob:**
- Receives circuit
- Participates in OT
- **Evaluates** the garbled circuit
- Sends result and runs verification

### 🧪 Verification

A post-processing step compares the MPC result with a local computation to verify **correctness**.

### Structure 
Note that inputs and outputs folder are not present in the project, but here are shown so to facilitate the comprension of files.

├── circuits/
│   ├── max_4_num.json
│   ├── max_8_num.json
│   ├── max_16_num.json
│   └── max_32_num.json
├── inputs/
│   ├── Alice.txt
│   └── Bob.txt
├── outputs/
│   ├── output_alice_bob.json
│   ├── alice_ot_side.txt
│   └── bob_ot_side.txt
├── main.py
├── alice.py
├── bob.py
├── yaoGarbler.py
├── yao.py
├── ot.py
├── util.py
├── createCircuitExtended.py
├── requirements.txt
├── README.md
└── .gitignore

### 🧱 Create New Circuit

To generate a new circuit, run the following command:

```bash
python createCircuitExtended.py
```

Make sure to adjust the top of the file to customize:
- `NUM_INPUT_TO_CONFRONT`
- `NAME_OUTPUT_CIRCUIT`



