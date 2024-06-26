"""IR code generator for converting MyPL to VM Instructions. 

NAME: David Giacobbi
DATE: Spring 2024
CLASS: CPSC 326

"""

from mypl_token import *
from mypl_ast import *
from mypl_var_table import *
from mypl_frame import *
from mypl_opcode import *
from mypl_vm import *


class CodeGenerator (Visitor):

    def __init__(self, vm):
        """Creates a new Code Generator given a VM. 
        
        Args:
            vm -- The target vm.
        """
        # the vm to add frames to
        self.vm = vm
        # the current frame template being generated
        self.curr_template = None
        # for var -> index mappings wrt to environments
        self.var_table = VarTable()
        # struct name -> StructDef for struct field info
        self.struct_defs = {}

    
    def add_instr(self, instr):
        """Helper function to add an instruction to the current template."""
        self.curr_template.instructions.append(instr)

        
    def visit_program(self, program):
        for struct_def in program.struct_defs:
            struct_def.accept(self)
        for fun_def in program.fun_defs:
            fun_def.accept(self)

    
    def visit_struct_def(self, struct_def):
        # remember the struct def for later
        self.struct_defs[struct_def.struct_name.lexeme] = struct_def

        
    def visit_fun_def(self, fun_def):
        # Create a new frame
        self.curr_template = VMFrameTemplate(fun_def.fun_name.lexeme, len(fun_def.params), []) 
        # Push new variable environment
        self.var_table.push_environment()
        # Store each argument provided on operand stack
        for param in fun_def.params:
            self.add_instr(STORE(self.var_table.total_vars))
            self.var_table.add(param.var_name.lexeme)
        # Visit each statement node
        for stmt in fun_def.stmts:
            stmt.accept(self)
        # Add return if last statement is not a return
        if fun_def.return_type.type_name.token_type == TokenType.VOID_TYPE:
            self.add_instr(PUSH(None))
            self.add_instr(RET())
        # Pop the variable environment
        self.var_table.pop_environment()
        # Add the frame to the VM
        self.vm.add_frame_template(self.curr_template)   

    
    def visit_return_stmt(self, return_stmt):
        # Push value from expression onto stack for return
        return_stmt.expr.accept(self)
        # Add instruction call to list
        self.add_instr(RET())

        
    def visit_var_decl(self, var_decl):
        # Check if list variable declaration
        if var_decl.var_def.data_type.is_list:
            self.add_instr(ALLOCL())
        else:
            # Check if expression value exists
            if var_decl.expr == None:
                self.add_instr(PUSH(None))
            else:
                var_decl.expr.accept(self)
        # Store expression value in memory
        self.add_instr(STORE(self.var_table.total_vars))
        # Add variable name to current environment
        self.var_table.add(var_decl.var_def.var_name.lexeme)
    

    def visit_list_fun_stmt(self, list_fun_stmt):
        # Take care of the list path to the list to find the max or min of
        # Load the first variable value
        var_val = self.var_table.get(list_fun_stmt.list_path[0].var_name.lexeme)
        self.add_instr(LOAD(var_val))
        # Check array expression
        if list_fun_stmt.list_path[0].array_expr != None:
            list_fun_stmt.list_path[0].array_expr.accept(self)
            self.add_instr(GETI())
        # Check if path is greater than 1 and proceed with remaining path
        if len(list_fun_stmt.list_path) > 0:
            # Follow the rest of the path
            for i in range(1, len(list_fun_stmt.list_path)):
                var_val = list_fun_stmt.list_path[i].var_name.lexeme
                self.add_instr(GETF(var_val))
                # Check array expression
                if list_fun_stmt.list_path[i].array_expr != None:
                    list_fun_stmt.list_path[i].array_expr.accept(self)
                    self.add_instr(GETI()) 

        # Use list function class to check which function
        if list_fun_stmt.function.token_type == TokenType.APPEND:
            # Convert to append value with visitor
            list_fun_stmt.append_item.accept(self)
            # Append value to the list
            self.add_instr(APP())
        elif list_fun_stmt.function.token_type == TokenType.CLEAR:
            self.add_instr(CLEAR())
        else:
            self.add_instr(POPL())

    
    def visit_assign_stmt(self, assign_stmt):
        # Load the first variable value
        var_val = self.var_table.get(assign_stmt.lvalue[0].var_name.lexeme)
        # Check if path is greater than 1 and proceed with remaining path
        if len(assign_stmt.lvalue) > 1:
            # Load the first var_val
            self.add_instr(LOAD(var_val))
            # Check array expression
            if assign_stmt.lvalue[0].array_expr != None:
                assign_stmt.lvalue[0].array_expr.accept(self)
                self.add_instr(GETI())
            # Follow the rest of the path
            for i in range(1, len(assign_stmt.lvalue)):
                if i == len(assign_stmt.lvalue)-1:
                    # Check array expression
                    if assign_stmt.lvalue[i].array_expr != None:
                        # Get the oid
                        self.add_instr(GETF(assign_stmt.lvalue[i].var_name.lexeme))
                        # Push the index
                        assign_stmt.lvalue[i].array_expr.accept(self)
                        # Visit the expression
                        assign_stmt.expr.accept(self)
                        # Set the index
                        self.add_instr(SETI())
                    else:
                        # Visit the expression
                        assign_stmt.expr.accept(self)
                        self.add_instr(SETF(assign_stmt.lvalue[i].var_name.lexeme)) 
                else:
                    var_val = assign_stmt.lvalue[i].var_name.lexeme
                    self.add_instr(GETF(var_val))
                    # Check array expression
                    if assign_stmt.lvalue[i].array_expr != None:
                        assign_stmt.lvalue[i].array_expr.accept(self)
                        self.add_instr(GETI()) 
        else: 
            # Check to set array or update value
            if assign_stmt.lvalue[0].array_expr != None:
                # Load the oid
                self.add_instr(LOAD(var_val))
                # Push the index
                assign_stmt.lvalue[0].array_expr.accept(self) 
                # Visit the expression
                assign_stmt.expr.accept(self)
                self.add_instr(SETI())
            else:
                # Visit the expression
                assign_stmt.expr.accept(self)
                self.add_instr(STORE(var_val))

    
    def visit_while_stmt(self, while_stmt):
        # Grab the starting index of the first instruction
        first_idx = len(self.curr_template.instructions)
        # Call while condition visitor
        while_stmt.condition.accept(self)
        # Create and add a JMPF instruction with temp operand -1 (jump to end)
        self.add_instr(JMPF(-1))
        temp = len(self.curr_template.instructions)-1
        # Push an environemnt in var table
        self.var_table.push_environment()
        # Visit all of the statments
        for stmt in while_stmt.stmts:
            stmt.accept(self)
        # Pop an environment in var table
        self.var_table.pop_environment()
        # Add a JMP instruction (to jump to starting index)
        self.add_instr(JMP(first_idx))
        # Add a NOP instruction (for JMPF to refer to)
        self.add_instr(NOP())
        # Update the JMPF instruction to refer to the NOP
        self.curr_template.instructions[temp] = JMPF(len(self.curr_template.instructions)-1)

        
    def visit_for_stmt(self, for_stmt):
        # Push an environment first for var decl
        self.var_table.push_environment()
        # Generate var decl
        for_stmt.var_decl.accept(self)
        # Call condition visitor and save index of conditional check
        condition_idx = len(self.curr_template.instructions)
        for_stmt.condition.accept(self)
        # Create and add a JMPF instruction with temp operand -1 (jump to end)
        self.add_instr(JMPF(-1))
        temp = len(self.curr_template.instructions)-1
        # Visit each of the statements
        for stmt in for_stmt.stmts:
            stmt.accept(self)
        # Visit the assign statement
        for_stmt.assign_stmt.accept(self)
        # Pop the environment
        self.var_table.pop_environment()
        # Add a JMP instruction (to jump to starting index)
        self.add_instr(JMP(condition_idx))
        # Add a NOP instruction (for JMPF to refer to)
        self.add_instr(NOP())
        # Update the JMPF instruction to refer to the NOP
        self.curr_template.instructions[temp] = JMPF(len(self.curr_template.instructions)-1)

    
    def visit_if_stmt(self, if_stmt):
        # Save final NOP jump indices to go to in successful case
        final_jmps = []
        # IF-PART
        # Push new environment
        self.var_table.push_environment()
        # Visit condition
        if_stmt.if_part.condition.accept(self)
        # Add a JMPF instruction with temp operand and save idx in list
        self.add_instr(JMPF(-1))
        temp = len(self.curr_template.instructions)-1
        # Visit stmts for if part
        for stmt in if_stmt.if_part.stmts:
            stmt.accept(self)
        # Pop environment
        self.var_table.pop_environment()
        # Jump to end of the if statement NOP and save idx
        self.add_instr(JMP(-1))
        final_jmps.append(len(self.curr_template.instructions)-1)
        # Create NOP to jump and update JUMPF instruction
        self.add_instr(NOP())
        self.curr_template.instructions[temp] = JMPF(len(self.curr_template.instructions)-1)
        # ELSE-IF PART
        # Iterate through each of the else if statements
        for else_if in if_stmt.else_ifs:
            # Push new environment
            self.var_table.push_environment()
            # Visit condition
            else_if.condition.accept(self)
            # Add a JMPF instruction with temp operand and save idx in list
            self.add_instr(JMPF(-1))
            temp = len(self.curr_template.instructions)-1
            # Visit stmts for if part
            for stmt in else_if.stmts:
                stmt.accept(self)
            # Pop environment
            self.var_table.pop_environment()
            # Jump to end of the if statement NOP and save idx
            self.add_instr(JMP(-1))
            final_jmps.append(len(self.curr_template.instructions)-1)
            # Create NOP to jump and update JUMPF instruction
            self.add_instr(NOP())
            self.curr_template.instructions[temp] = JMPF(len(self.curr_template.instructions)-1)     
        # ELSE PART
        # Check if else statement exists
        if if_stmt.else_stmts != None:
            # Push new environment
            self.var_table.push_environment()
            # Visit each statment
            for stmt in if_stmt.else_stmts:
                stmt.accept(self)
            # Pop environment
            self.var_table.pop_environment()
        # FINAL JUMP PART     
        # Add final NOP and update JMP calls for true statements
        self.add_instr(NOP())
        for idx in final_jmps:
            self.curr_template.instructions[idx] = JMP(len(self.curr_template.instructions)-1)
            
    
    def visit_call_expr(self, call_expr):
        # Create special cases for all of the MyPL built-in functions
        # Print Built-In
        if call_expr.fun_name.lexeme == 'print':
            if len(call_expr.args) > 0:
                call_expr.args[0].accept(self)
            self.add_instr(WRITE())
        # Input Built-In
        elif call_expr.fun_name.lexeme == 'input':
            self.add_instr(READ())
        # ITOS Built-In
        elif call_expr.fun_name.lexeme == "itos":
            call_expr.args[0].accept(self)
            self.add_instr(TOSTR())
        # ITOD Built-In
        elif call_expr.fun_name.lexeme == "itod":
            call_expr.args[0].accept(self)
            self.add_instr(TODBL())
        # DTOS Built-In
        elif call_expr.fun_name.lexeme == "dtos":
            call_expr.args[0].accept(self)
            self.add_instr(TOSTR())
        # DTOI Built-In
        elif call_expr.fun_name.lexeme == "dtoi":
            call_expr.args[0].accept(self)
            self.add_instr(TOINT())
        # STOI Built-In
        elif call_expr.fun_name.lexeme == "stoi":
            call_expr.args[0].accept(self)
            self.add_instr(TOINT())
        # STOD Built-In
        elif call_expr.fun_name.lexeme == "stod":
            call_expr.args[0].accept(self)
            self.add_instr(TODBL())
        # Length Built-In
        elif call_expr.fun_name.lexeme == "length":
            call_expr.args[0].accept(self)
            self.add_instr(LEN())
        # Get Built-In
        elif call_expr.fun_name.lexeme == "get":
            call_expr.args[0].accept(self)
            call_expr.args[1].accept(self)
            self.add_instr(GETC())
        # Create function call for specified name
        else:
            # Push arguments onto stack
            for arg in call_expr.args:
                arg.accept(self)
            # Create function call
            self.add_instr(CALL(call_expr.fun_name.lexeme))

        
    def visit_expr(self, expr):
        # Add the first term
        expr.first.accept(self)
        # Check if there is more to the expression
        if expr.op != None:
            # Push the rest of the expression
            expr.rest.accept(self)
            # Add the proper instruction for the op
            if expr.op.token_type == TokenType.PLUS:
                self.add_instr(ADD())
            elif expr.op.token_type == TokenType.MINUS:
                self.add_instr(SUB())
            elif expr.op.token_type == TokenType.TIMES:
                self.add_instr(MUL())
            elif expr.op.token_type == TokenType.DIVIDE:
                self.add_instr(DIV())
            elif expr.op.token_type == TokenType.AND:
                self.add_instr(AND())
            elif expr.op.token_type == TokenType.OR:
                self.add_instr(OR())
            elif expr.op.token_type == TokenType.LESS:
                self.add_instr(CMPLT())
            elif expr.op.token_type == TokenType.LESS_EQ:
                self.add_instr(CMPLE())
            elif expr.op.token_type == TokenType.EQUAL:
                self.add_instr(CMPEQ())
            elif expr.op.token_type == TokenType.NOT_EQUAL:
                self.add_instr(CMPNE())
            elif expr.op.token_type == TokenType.GREATER:
                self.add_instr(CMPLE())
                self.add_instr(NOT())
            elif expr.op.token_type == TokenType.GREATER_EQ:
                self.add_instr(CMPLT())
                self.add_instr(NOT())
        # Check if not_op is true
        if expr.not_op == True:
            self.add_instr(NOT())

            
    def visit_data_type(self, data_type):
        # nothing to do here
        pass

    
    def visit_var_def(self, var_def):
        # nothing to do here
        pass

    
    def visit_simple_term(self, simple_term):
        simple_term.rvalue.accept(self)

        
    def visit_complex_term(self, complex_term):
        complex_term.expr.accept(self)

        
    def visit_simple_rvalue(self, simple_rvalue):
        val = simple_rvalue.value.lexeme
        if simple_rvalue.value.token_type == TokenType.INT_VAL:
            self.add_instr(PUSH(int(val)))
        elif simple_rvalue.value.token_type == TokenType.DOUBLE_VAL:
            self.add_instr(PUSH(float(val)))
        elif simple_rvalue.value.token_type == TokenType.STRING_VAL:
            val = val.replace('\\n', '\n')
            val = val.replace('\\t', '\t')
            self.add_instr(PUSH(val))
        elif val == 'true':
            self.add_instr(PUSH(True))
        elif val == 'false':
            self.add_instr(PUSH(False))
        elif val == 'null':
            self.add_instr(PUSH(None))

    
    def visit_new_rvalue(self, new_rvalue):
        # Check if type a struct
        if new_rvalue.struct_params != None:
            # Allocate instruction
            self.add_instr(ALLOCS())
            # Get the field information from struct def
            new_struct = self.struct_defs[new_rvalue.type_name.lexeme]
            # Set each field in the struct with provided struct_params
            for i in range(len(new_rvalue.struct_params)):
                self.add_instr(DUP())
                new_rvalue.struct_params[i].accept(self)
                self.add_instr(SETF(new_struct.fields[i].var_name.lexeme))
        # Type is an array creation
        else:
            # Get the size of the array from expression
            new_rvalue.array_expr.accept(self)
            # Allocate instruction
            self.add_instr(ALLOCA())


    def visit_list_rvalue(self, list_rvalue):
        # Take care of the list path to the list to find the max or min of
        # Load the first variable value
        var_val = self.var_table.get(list_rvalue.list_path[0].var_name.lexeme)
        self.add_instr(LOAD(var_val))
        # Check array expression
        if list_rvalue.list_path[0].array_expr != None:
            list_rvalue.list_path[0].array_expr.accept(self)
            self.add_instr(GETI())
        # Check if path is greater than 1 and proceed with remaining path
        if len(list_rvalue.list_path) > 0:
            # Follow the rest of the path
            for i in range(1, len(list_rvalue.list_path)):
                var_val = list_rvalue.list_path[i].var_name.lexeme
                self.add_instr(GETF(var_val))
                # Check array expression
                if list_rvalue.list_path[i].array_expr != None:
                    list_rvalue.list_path[i].array_expr.accept(self)
                    self.add_instr(GETI()) 

        # Perform max or min function depending on which is found in AST node
        if list_rvalue.fun_name.token_type == TokenType.MAX:
            self.add_instr(MAX())
        else:
            self.add_instr(MIN())
                
    
    def visit_var_rvalue(self, var_rvalue):
        # Load the first variable value
        var_val = self.var_table.get(var_rvalue.path[0].var_name.lexeme)
        self.add_instr(LOAD(var_val))
        # Check array expression
        if var_rvalue.path[0].array_expr != None:
            var_rvalue.path[0].array_expr.accept(self)
            self.add_instr(GETI())
        # Check if path is greater than 1 and proceed with remaining path
        if len(var_rvalue.path) > 0:
            # Follow the rest of the path
            for i in range(1, len(var_rvalue.path)):
                var_val = var_rvalue.path[i].var_name.lexeme
                self.add_instr(GETF(var_val))
                # Check array expression
                if var_rvalue.path[i].array_expr != None:
                    var_rvalue.path[i].array_expr.accept(self)
                    self.add_instr(GETI())             
                
