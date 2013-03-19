from lazyflow.graph import Operator, InputSlot, OutputSlot
from lazyflow.operators import OpInterpMissingData, OpBlockedArrayCache

class OpFillMissingSlices(Operator):
    Input = InputSlot()
    
    Output = OutputSlot()
    CachedOutput = OutputSlot()
    
    def __init__(self, *args, **kwargs):
        super( self.__class__, self ).__init__(*args, **kwargs)
        
        # Set up interpolation
        self._opInterp = OpInterpMissingData( parent=self )
        self._opInterp.InputVolume.connect( self.Input )

        # The cache serves two purposes:
        # 1) Determine shape of accesses to the interpolation operator
        # 2) Avoid duplicating work
        self._opCache = OpBlockedArrayCache( parent=self )
        self._opCache.Input.connect( self._opInterp.Output )
        self._opCache.fixAtCurrent.setValue( False )

        # Regular output is for headless operation,
        # Cached output is for the GUI        
        self.Output.connect( self._opInterp.Output )
        self.CachedOutput.connect( self._opCache.Output )
        
    def setupOutputs(self):
        blockdims = { 't' : 1,
                      'x' : 256,
                      'y' : 256,
                      'z' : 100,
                      'c' : 1 }
        blockshape = map( blockdims.get, self.Input.meta.getTaggedShape().keys() )        
        self._opCache.innerBlockShape.setValue( tuple(blockshape) )        
        self._opCache.outerBlockShape.setValue( tuple(blockshape) )

    def execute(self, slot, subindex, roi, result):
        assert False, "Shouldn't get here"
    
    def propagateDirty(self, slot, subindex, roi):
        pass # Nothing to do here.

