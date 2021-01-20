from DialogFrameSimple import DialogFrameSimple
from DialogAct import DialogAct
from DialogActTypes import DialogActTypes

class FrameDMSimple:

    def __init__(self, NLU, NLG):
        self.NLU = NLU
        self.NLG = NLG
        # define frame below, for example:
        self.DialogFrame = DialogFrameSimple()

    def execute(self, inputStr):
        # apply the NLU component
        currentSemanticFrame = self.NLU.parse(inputStr)

        # update the dialog frame with the new information
        self.trackState(currentSemanticFrame)

        # and decide what to do next
        newDialogAct = self.selectDialogAct()

        # then generate some meaningful response
        response = self.NLG.generate(newDialogAct) 
        return response

    def trackState(self, newSemanticFrame):
        # update self.DialogFrame based on the contents of newSemanticFrame
        return

    def selectDialogAct(self):
        # decide on what dialog act to execute

        # by default, return a Hello dialog act
        dialogAct = DialogAct()
        dialogAct.DialogActType = DialogActTypes.HELLO
        return dialogAct
