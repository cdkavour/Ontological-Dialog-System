import argparse
from NLUDefault import NLUDefault
from NLGDefault import NLGDefault
from NLGForFrame import NLGForFrame
from NLUForFrame import NLUForFrame
from FSM import FSM
from FrameDMSimple import FrameDMSimple
from FrameDMExtended import FrameDMExtended

def main():
    parser = argparse.ArgumentParser("Homework 1 dialog manager system")
    parser.add_argument("-v", "--verbose", action="count", default=0)
    parser.add_argument("-s", "--system", choices=["FSM", "FrameSimple", "FrameExtended"])
    parser.add_argument("-u", "--universals", action="store_true",
                        help="for FSM, add universals")
    parser.add_argument("-l", "--NLU", default="Default")
    parser.add_argument("-g", "--NLG", default="Default")
    args = parser.parse_args()
    
    system = args.system;
    NLU = args.NLU;
    NLG = args.NLG;
    universals = args.universals

    print("NLU = {}, system = {}, NLG = {}".format(NLU, system, NLG))
   
    NLUModule = None
    DMModule = None
    NLGModule = None

    if (NLU == "Default"):
        NLUModule = NLUDefault()
    if (NLG == "Default"):
        NLGModule = NLGDefault()

    # the frame system should use its own NLx system
    if system == "FrameSimple" or system == "FrameExtended":
        NLUModule = NLUForFrame()
        NLGModule = NLGForFrame()

    if (system == "FSM"):
        DMModule = FSM(NLUModule, NLGModule,universals)
    elif (system == "FrameSimple"):
        DMModule = FrameDMSimple(NLUModule, NLGModule)
    elif (system == "FrameExtended"):
        DMModule = FrameDMExtended(NLUModule, NLGModule)
    else:
        print("{} not implemented".format(system))
        return
 
    print("Welcome to the HW1 Dialog System")
    if system == "FSM":
        output = DMModule.execute('')
        print(output)
    while(True):
        inputStr = input("> ")
        print(inputStr)
        if (inputStr == "Quit"):
            break
        outputStr = DMModule.execute(inputStr)
        print(outputStr)

        if ("goodbye" in outputStr.lower()):
            break
        

if __name__ == "__main__":
    main()
