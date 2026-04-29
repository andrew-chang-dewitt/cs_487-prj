"""Errors that can be raised at the Application layer."""

from inspect import stack
from typing import Optional

from .optional import some_or_default


class TodoError(NotImplementedError):
    """Raise when stubbing out methods/behaviour that isn't built yet."""

    prefix: str = "TODO!"

    msg: str
    funqname: str
    filename: str
    linenum: int
    codectx: list[str]

    def __init__(self, msg: Optional[str] = None) -> None:
        curr_stack = stack()
        caller = curr_stack[1]

        self.filename = caller.filename
        self.linenum = caller.lineno
        self.codectx: list[str] = some_or_default(caller.code_context, [])

        funname = caller.function
        funobj = caller.frame.f_globals.get(funname)
        try:
            if "self" in caller.frame.f_locals:
                instance = caller.frame.f_locals["self"]
                funobj = getattr(instance.__class__, funname, funobj)

            self.funqname = getattr(funobj, "__qualname__", funname)
        except Exception:
            self.funqname = funname

        loc = f"[{self.funqname}@{self.filename}:{self.linenum}] "
        self.msg = loc
        indent = " " * len(loc)

        self.msg += " " + TodoError.prefix
        if msg:
            self.msg += f": {msg}\n\n"

        if len(self.codectx) > 0:
            for line in self.codectx[1:]:
                self.msg += f"  {indent}{line}"

        super().__init__(self.msg)

    def __repr__(self) -> str:
        out = f"    msg={repr(self.msg)}\n"
        out += f"    funqname={repr(self.funqname)}\n"
        out += f"    filename={repr(self.filename)}\n"
        out += f"    linenum={repr(self.linenum)}\n"
        out += f"    codectx=[{'        ,\n'.join(self.codectx)}]\n"

        return f"TodoError(\n{out})"
