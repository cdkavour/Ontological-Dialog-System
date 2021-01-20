import argparse
from NLUDefault import NLUDefault
from NLGDefault import NLGDefault
from FSM import FSM
from FrameDMSimple import FrameDMSimple
from FrameDMExtended import FrameDMExtended

def main():
    parser = argparse.ArgumentParser("Homework 1 dialog manager system")
    parser.add_argument("-v", "--verbose", action="count", default=0)
    parser.add_argument("-s", "--system", choices=["FSM", "FrameSimple", "FrameExtended"])
    parser.add_argument("-l", "--NLU", default="Default")
    parser.add_argument("-g", "--NLG", default="Default")
    args = parser.parse_args()
    
    system = args.system;
    NLU = args.NLU;
    NLG = args.NLG;
    
    print("NLU = {}, system = {}, NLG = {}".format(NLU, system, NLG))
   
    NLUModule = None
    DMModule = None
    NLGModule = None

    if (NLU == "Default"):
        NLUModule = NLUDefault()

    if (NLG == "Default"):
        NLGModule = NLGDefault()

    if (system == "FSM"):
        DMModule = FSM(NLUModule, NLGModule)
    elif (system == "FrameSimple"):
        DMModule = FrameDMSimple(NLUModule, NLGModule)
    elif (system == "FrameExtended"):
        DMModule = FrameDMExtended(NLUModule, NLGModule)
    else:
        print("{} not implemented".format(system))
        return
 
    print("Welcome to the HW1 Dialog System")
    while(True):
        inputStr = input("> ")
        if (inputStr == "Quit"):
            break

        outputStr = DMModule.execute(inputStr)

        print(outputStr)
        

if __name__ == "__main__":
    main()
