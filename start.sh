export PATH="./ScratchABit:$PATH"
cp ./ida-xtensa2/xtensa.py ./ScratchABit/plugins/cpu/xtensa.py
PYTHONPATH=. ScratchABit.py tuya.def --script clean_init
