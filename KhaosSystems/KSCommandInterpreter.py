from .KSBasicTypes import KSVector

import importlib

class KSEntityHandle(object):
    name: str = None
    def __init__(self, name: str) -> None:
        self.name = name        

class KSMayaEntityHandle(KSEntityHandle):
    def __init__(self, name: str) -> None:
        super().__init__(name)

class KSCommandInterpreter(object):
    def Exists(self, name: str) -> bool:
        print("Exists()")
        print(f" - name: {name}")

    def Delete(self, name: str) -> None:
        print("Delete()")
        print(f" - name: {name}")

    def CreateJoint(self, name: str, parent: KSEntityHandle = None, position: KSVector = None) -> KSEntityHandle:
        print("CreateJoint()")
        print(f" - name: {name}")
        if (parent != None):
            print(f" - parent: {parent.name}")
        if (position != None):
            print(f" - position: {position.x}, {position.y}, {position.z}")

        return KSEntityHandle(name)

    def Parent(self, parent: KSEntityHandle, child: KSEntityHandle) -> None:
        print("Parent()")
        print(f" - parent: {parent.name}")
        print(f" - child: {child.name}")

class KSMayaCommandInterpreter(KSCommandInterpreter):
    mayaCmds = None

    def __init__(self) -> None:
        super().__init__()
        self.mayaCmds = importlib.import_module("maya.cmds")

    def Exists(self, name: str) -> bool:
        return bool(self.mayaCmds.objExists(name))

    def Delete(self, name: str) -> None:
        if (self.Exists(name)):
            self.mayaCmds.delete(name)

    def CreateJoint(self, name: str, parent: KSEntityHandle = None, position: KSVector = None) -> KSMayaEntityHandle:
        jnt = self.mayaCmds.createNode("joint", name=name)
        jntHandle = KSMayaEntityHandle(jnt)

        if (parent != None):
            self.Parent(parent=parent, child=jntHandle)

        if (position != None):
            self.mayaCmds.xform([jnt], translation=(position.x, position.y, position.z))

        return jntHandle

    def Parent(self, parent: KSEntityHandle, child: KSEntityHandle) -> None:
        if (not self.Exists(parent.name)):
            print("Error: parent object did not exist.")
            return
        
        if (not self.Exists(parent.name)):
            print("Error: child object did not exist.")
            return

        self.mayaCmds.parent(child.name, parent.name)