"""Implementation of the MyPL Virtual Machine (VM).

NAME: David Giacobbi
DATE: Spring 2024
CLASS: CPSC 326

"""

from mypl_error import *
from mypl_opcode import *
from mypl_frame import *


class VM:

    def __init__(self):
        """Creates a VM."""
        self.struct_heap = {}        # id -> dict
        self.array_heap = {}         # id -> list
        self.next_obj_id = 2024      # next available object id (int)
        self.frame_templates = {}    # function name -> VMFrameTemplate
        self.call_stack = []         # function call stack

    
    def __repr__(self):
        """Returns a string representation of frame templates."""
        s = ''
        for name, template in self.frame_templates.items():
            s += f'\nFrame {name}\n'
            i = 0
            for instr in template.instructions:
                s += f'  {i}: {instr}\n'
                i += 1
        return s

    
    def add_frame_template(self, template):
        """Add the new frame info to the VM. 

        Args: 
            frame -- The frame info to add.

        """
        self.frame_templates[template.function_name] = template

    
    def error(self, msg, frame=None):
        """Report a VM error."""
        if not frame:
            raise VMError(msg)
        pc = frame.pc - 1
        instr = frame.template.instructions[pc]
        name = frame.template.function_name
        msg += f' (in {name} at {pc}: {instr})'
        raise VMError(msg)

    
    #----------------------------------------------------------------------
    # RUN FUNCTION
    #----------------------------------------------------------------------
    
    def run(self, debug=False):
        """Run the virtual machine."""

        # grab the "main" function frame and instantiate it
        if not 'main' in self.frame_templates:
            self.error('No "main" functrion')
        frame = VMFrame(self.frame_templates['main'])
        self.call_stack.append(frame)

        # run loop (continue until run out of call frames or instructions)
        while self.call_stack and frame.pc < len(frame.template.instructions):
            # get the next instruction
            instr = frame.template.instructions[frame.pc]
            # increment the program count (pc)
            frame.pc += 1
            # for debugging:
            if debug:
                print('\n')
                print('\t FRAME.........:', frame.template.function_name)
                print('\t PC............:', frame.pc)
                print('\t INSTRUCTION...:', instr)
                val = None if not frame.operand_stack else frame.operand_stack[-1]
                print('\t NEXT OPERAND..:', val)
                cs = self.call_stack
                fun = cs[-1].template.function_name if cs else None
                print('\t NEXT FUNCTION..:', fun)

            #------------------------------------------------------------
            # Literals and Variables
            #------------------------------------------------------------

            if instr.opcode == OpCode.PUSH:
                frame.operand_stack.append(instr.operand)

            elif instr.opcode == OpCode.POP:
                frame.operand_stack.pop()
                
            # LOAD Operation
            elif instr.opcode == OpCode.LOAD:
                x = frame.variables[instr.operand]
                frame.operand_stack.append(x)
                
            # STORE Operation
            elif instr.opcode == OpCode.STORE:
                x = frame.operand_stack.pop()
                if instr.operand == len(frame.variables):
                    frame.variables.append(x)
                else:
                    frame.variables[instr.operand] = x
            
            #------------------------------------------------------------
            # Operations
            #------------------------------------------------------------

            # ADD Operation
            elif instr.opcode == OpCode.ADD:
                # Pop x and y values
                x = frame.operand_stack.pop()
                y = frame.operand_stack.pop()
                # Check for null values
                if x == None or y == None:
                    self.error('operand stack cannot add null values', frame)
                # Push valid sum onto stack
                sum = y + x
                frame.operand_stack.append(sum)
            
            # SUB Operation
            elif instr.opcode == OpCode.SUB:
                # Pop x and y values
                x = frame.operand_stack.pop()
                y = frame.operand_stack.pop()
                # Check for null values
                if x == None or y == None:
                    self.error('operand stack cannot subtract null values', frame)
                # Push valid difference onto stack
                diff = y - x
                frame.operand_stack.append(diff)
            
            # MUL Operation
            elif instr.opcode == OpCode.MUL:
                # Pop x and y values
                x = frame.operand_stack.pop()
                y = frame.operand_stack.pop()
                # Check for null values
                if x == None or y == None:
                    self.error('operand stack cannot multiply null values', frame)
                # Push valid product onto stack
                product = y * x
                frame.operand_stack.append(product)
            
            # DIV Operation
            elif instr.opcode == OpCode.DIV:
                # Pop x and y values
                x = frame.operand_stack.pop()
                y = frame.operand_stack.pop()
                # Check for null values
                if x == None or y == None:
                    self.error('operand stack cannot divide null values', frame)
                if x == 0:
                    self.error('cannot divide by zero', frame)
                # Push valid quotient onto stack
                if type(x) == int and type(y) == int:
                    quotient = int(y / x)
                elif type(x) == float and type(y) == float:
                    quotient = y / x
                else:
                    self.error('only can divide int or double values', frame)
                frame.operand_stack.append(quotient)
            
            # AND Operation
            elif instr.opcode == OpCode.AND:
                # Pop x and y values
                x = frame.operand_stack.pop()
                y = frame.operand_stack.pop()
                # Check for null values
                if x == None or y == None:
                    self.error('operand stack cannot AND null values', frame)
                # Push result onto stack
                result = y and x
                frame.operand_stack.append(result)
            
            # OR Operation
            elif instr.opcode == OpCode.OR:
                # Pop x and y values
                x = frame.operand_stack.pop()
                y = frame.operand_stack.pop()
                # Check for null values
                if x == None or y == None:
                    self.error('operand stack cannot OR null values', frame)
                # Push result onto stack
                result = y or x
                frame.operand_stack.append(result)
            
            # NOT Operation
            elif instr.opcode == OpCode.NOT:
                # Pop x and y values
                x = frame.operand_stack.pop()
                # Check for null values
                if x == None:
                    self.error('operand stack cannot NOT null values', frame)
                # Push result onto stack
                result = not x
                frame.operand_stack.append(result)
            
            # CMPLT Operation
            elif instr.opcode == OpCode.CMPLT:
                # Pop x and y values
                x = frame.operand_stack.pop()
                y = frame.operand_stack.pop()
                # Check for null values
                if x == None or y == None:
                    self.error('operand stack cannot compare null values', frame)
                # Push result onto stack
                result = y < x
                frame.operand_stack.append(result)
            
            # CMPLE Operation
            elif instr.opcode == OpCode.CMPLE:
                # Pop x and y values
                x = frame.operand_stack.pop()
                y = frame.operand_stack.pop()
                # Check for null values
                if x == None or y == None:
                    self.error('operand stack cannot compare null values', frame)
                # Push result onto stack
                result = y <= x
                frame.operand_stack.append(result)
            
            # CMPEQ Operation
            elif instr.opcode == OpCode.CMPEQ:
                # Pop x and y values
                x = frame.operand_stack.pop()
                y = frame.operand_stack.pop()
                # Push result onto stack
                result = y == x
                frame.operand_stack.append(result)
            
            # CMPNE Operation
            elif instr.opcode == OpCode.CMPNE:
                # Pop x and y values
                x = frame.operand_stack.pop()
                y = frame.operand_stack.pop()
                # Push result onto stack
                result = y != x
                frame.operand_stack.append(result)

            #------------------------------------------------------------
            # Branching
            #------------------------------------------------------------

            # JMP Operation
            elif instr.opcode == OpCode.JMP:
                # Check that operand is valid type
                if type(instr.operand) != int:
                    self.error('operand must be of integer type', frame)
                frame.pc = instr.operand

            # JMPF Operation
            elif instr.opcode == OpCode.JMPF:
                # Pop bool off stack
                x = frame.operand_stack.pop()
                if x == False:
                    # Check that operand is valid type
                    if type(instr.operand) != int:
                        self.error('operand must be of integer type', frame)
                    frame.pc = instr.operand            
                    
            #------------------------------------------------------------
            # Functions
            #------------------------------------------------------------

            # CALL Operation
            elif instr.opcode == OpCode.CALL:
                # Get stack frame info
                fun_name = instr.operand
                # Instantiate a new frame
                new_frame_template = self.frame_templates[fun_name]
                new_frame = VMFrame(new_frame_template)
                # Push it onto the frame call stack
                self.call_stack.append(new_frame)
                # Copy arg_count arguments into new_frame operand stack
                for i in range(new_frame.template.arg_count):
                    arg = frame.operand_stack.pop()
                    new_frame.operand_stack.append(arg)
                # Set current frame in VM to new_frame
                frame = new_frame
                    
            # RET Operation
            elif instr.opcode == OpCode.RET:
                # Grab return value
                return_val = frame.operand_stack.pop()
                # Pop frame
                self.call_stack.pop()
                # Check if frame exists now
                if len(self.call_stack) != 0:
                    frame = self.call_stack[-1]
                    frame.operand_stack.append(return_val)
            
            #------------------------------------------------------------
            # Built-In Functions
            #------------------------------------------------------------

            # WRITE Operation
            elif instr.opcode == OpCode.WRITE:
                x = frame.operand_stack.pop()
                # Check if x is a null variable
                if x == None:
                    print('null', end='')
                elif x == True and type(x) == bool:
                    print('true', end='')
                elif x == False and type(x) == bool:
                    print('false', end='')
                else:
                    print(x, end='')
            
            # READ Operation
            elif instr.opcode == OpCode.READ:
                # Read from stdin and push
                x = input()
                frame.operand_stack.append(x)

            # LEN Operation
            elif instr.opcode == OpCode.LEN:
                # Pop x
                x = frame.operand_stack.pop()
                # Check if type is string
                if type(x) == str:
                    length = len(x)
                    frame.operand_stack.append(length)
                # Else push oid
                else:
                    if x in self.struct_heap:
                        frame.operand_stack.append(len(self.struct_heap[x]))
                    elif x in self.array_heap:
                        frame.operand_stack.append(len(self.array_heap[x]))
                    else:
                        self.error('cannot identify length of current object on stack', frame)

            # GETC Operation
            elif instr.opcode == OpCode.GETC:
                # Pop string x and index y
                x = frame.operand_stack.pop()
                y = frame.operand_stack.pop()
                # Check that x and y are valid
                if x == None or y == None:
                    self.error('cannot get character from null value', frame)
                if type(x) != str or type(y) != int or y < 0 or y >= len(x):
                    self.error('cannot reference string index with given stack', frame)
                # Push the character at index
                frame.operand_stack.append(x[y])

            # TOINT Operation
            elif instr.opcode == OpCode.TOINT:
                # Pop x value and convert
                x = frame.operand_stack.pop()
                try:
                    frame.operand_stack.append(int(x))
                except:
                    self.error('cannot convert to integer', frame)

            # TODBL Operation
            elif instr.opcode == OpCode.TODBL:
                # Pop x value and convert
                x = frame.operand_stack.pop()
                try:
                    frame.operand_stack.append(float(x))
                except:
                    self.error('cannot convert to double', frame)

            # TOSTR Operation
            elif instr.opcode == OpCode.TOSTR:
                # Pop x value and convert
                x = frame.operand_stack.pop()
                # Error check
                if x == None:
                    self.error("cannot convert to null to string", frame)
                try:
                    frame.operand_stack.append(str(x))
                except:
                    self.error('cannot convert to string', frame)

            
            #------------------------------------------------------------
            # Heap
            #------------------------------------------------------------

            # ALLOCS Operation
            elif instr.opcode == OpCode.ALLOCS:
                # Get the next oid
                oid = self.next_obj_id
                self.next_obj_id += 1
                # Allocate space and push oid on stack
                self.struct_heap[oid] = {}
                frame.operand_stack.append(oid)
            
            # SETF Operation
            elif instr.opcode == OpCode.SETF:
                # Pop value and oid
                x = frame.operand_stack.pop()
                y = frame.operand_stack.pop()
                # Ensure no null values
                if y == None:
                    self.error('operand stack cannot set null values', frame)
                # Set heap set
                self.struct_heap[y][instr.operand] = x
            
            # GETF Operation
            elif instr.opcode == OpCode.GETF:
                # Pop oid
                x = frame.operand_stack.pop()
                # Ensure no null values
                if x == None:
                    self.error('operand stack cannot get null values', frame)
                # Set heap set
                val = self.struct_heap[x][instr.operand]
                frame.operand_stack.append(val)
            
            # ALLOCA Operation
            elif instr.opcode == OpCode.ALLOCA:
                # Get oid and length
                oid = self.next_obj_id
                self.next_obj_id += 1
                # Check for valid array length value
                array_length = frame.operand_stack.pop()
                if type(array_length) != int or array_length < 0:
                    self.error('array length must be of integer type', frame)
                # Add to operand stack
                self.array_heap[oid] = [None for _ in range(array_length)]
                frame.operand_stack.append(oid)

            # SETI Operation
            elif instr.opcode == OpCode.SETI:
                # Pop value and oid
                x = frame.operand_stack.pop()
                y = frame.operand_stack.pop()
                z = frame.operand_stack.pop()
                # Ensure no null values
                if y == None or z == None:
                    self.error('operand stack cannot set null values', frame)
                # Index error
                if y < 0 or type(y) != int or y >= len(self.array_heap[z]):
                    self.error('invalid index call for array', frame)
                # Set heap set
                self.array_heap[z][y] = x

            # GETI Operation
            elif instr.opcode == OpCode.GETI:
                # Pop oid
                x = frame.operand_stack.pop()
                y = frame.operand_stack.pop()
                # Ensure no null values
                if x == None or y == None:
                    self.error('operand stack cannot get null values', frame)
                # Index error
                if x < 0 or type(x) != int or x >= len(self.array_heap[y]):
                    self.error('invalid index call for array', frame)
                # Set heap set
                val = self.array_heap[y][x]
                frame.operand_stack.append(val)


            #------------------------------------------------------------
            # List OpCode
            #------------------------------------------------------------

            # Allocate list ID operation
            elif instr.opcode == OpCode.ALLOCL:
                # Get oid=
                oid = self.next_obj_id
                self.next_obj_id += 1
                # Add to operand stack
                self.array_heap[oid] = []
                frame.operand_stack.append(oid)

            # Finding the max element in a list
            elif instr.opcode == OpCode.MAX:
                # Pop oid
                x = frame.operand_stack.pop()
                # Ensure no null values
                if x == None:
                    self.error('operand stack cannot get null values', frame)
                # Set heap set
                val = max(self.array_heap[x])
                frame.operand_stack.append(val)

            # Finding the min element in a list
            elif instr.opcode == OpCode.MIN:
                # Pop oid
                x = frame.operand_stack.pop()
                # Ensure no null values
                if x == None:
                    self.error('operand stack cannot get null values', frame)
                # Set heap
                val = min(self.array_heap[x])
                frame.operand_stack.append(val)

            # Setting a list back to the empty list []
            elif instr.opcode == OpCode.CLEAR:
                # Pop oid
                x = frame.operand_stack.pop()
                # Ensure no null values
                if x == None:
                    self.error('operand stack cannot get null values', frame)
                # Set heap
                self.array_heap[x] = []

            # Remove the last element of a list
            elif instr.opcode == OpCode.POPL:
                # Pop oid
                x = frame.operand_stack.pop()
                # Ensure no null values
                if x == None:
                    self.error('operand stack cannot get null values', frame)
                # Set heap
                list_length = len(self.array_heap[x])
                self.array_heap[x] = self.array_heap[x][0:(list_length-1)]

            # Append provided value to the list
            elif instr.opcode == OpCode.APP:
                # Pop value x, oid y
                x = frame.operand_stack.pop()
                y = frame.operand_stack.pop()
                # Ensure no null values
                if y == None:
                    self.error('operand stack cannot get null values', frame)
                # Set heap
                self.array_heap[y] = self.array_heap[y] + [x]

                        
            #------------------------------------------------------------
            # Special 
            #------------------------------------------------------------

            elif instr.opcode == OpCode.DUP:
                x = frame.operand_stack.pop()
                frame.operand_stack.append(x)
                frame.operand_stack.append(x)

            elif instr.opcode == OpCode.NOP:
                # do nothing
                pass

            else:
                self.error(f'unsupported operation {instr}')
