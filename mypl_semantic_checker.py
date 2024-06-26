"""Semantic Checker Visitor for semantically analyzing a MyPL program.

NAME: David Giacobbi
DATE: Spring 2024
CLASS: CPSC 326

"""

from dataclasses import dataclass
from mypl_error import *
from mypl_token import Token, TokenType
from mypl_ast import *
from mypl_symbol_table import SymbolTable


BASE_TYPES = ['int', 'double', 'bool', 'string']
BUILT_INS = ['print', 'input', 'itos', 'itod', 'dtos', 'dtoi', 'stoi', 'stod',
             'length', 'get']

class SemanticChecker(Visitor):
    """Visitor implementation to semantically check MyPL programs."""

    def __init__(self):
        self.structs = {}
        self.functions = {}
        self.symbol_table = SymbolTable()
        self.curr_type = None


    # Helper Functions

    def error(self, msg, token):
        """Create and raise a Static Error."""
        if token is None:
            raise StaticError(msg)
        else:
            m = f'{msg} near line {token.line}, column {token.column}'
            raise StaticError(m)


    def get_field_type(self, struct_def, field_name):
        """Returns the DataType for the given field name of the struct
        definition.

        Args:
            struct_def: The StructDef object 
            field_name: The name of the field

        Returns: The corresponding DataType or None if the field name
        is not in the struct_def.

        """
        for var_def in struct_def.fields:
            if var_def.var_name.lexeme == field_name:
                return var_def.data_type
        return None

        
    # Visitor Functions
    
    def visit_program(self, program):
        # check and record struct defs
        for struct in program.struct_defs:
            struct_name = struct.struct_name.lexeme
            if struct_name in self.structs:
                self.error(f'duplicate {struct_name} definition', struct.struct_name)
            self.structs[struct_name] = struct
        # check and record function defs
        for fun in program.fun_defs:
            fun_name = fun.fun_name.lexeme
            if fun_name in self.functions: 
                self.error(f'duplicate {fun_name} definition', fun.fun_name)
            if fun_name in BUILT_INS:
                self.error(f'redefining built-in function', fun.fun_name)
            if fun_name == 'main' and fun.return_type.type_name.lexeme != 'void':
                self.error('main without void type', fun.return_type.type_name)
            if fun_name == 'main' and fun.params: 
                self.error('main function with parameters', fun.fun_name)
            self.functions[fun_name] = fun
        # check main function
        if 'main' not in self.functions:
            self.error('missing main function', None)
        # check each struct
        for struct in self.structs.values():
            struct.accept(self)
        # check each function
        for fun in self.functions.values():
            fun.accept(self)
        
        
    def visit_struct_def(self, struct_def):
        # Push environment onto stack
        self.symbol_table.push_environment()
        # Check the fields for valid names
        for var_def in struct_def.fields:
            var_def.accept(self)
        # Pop environment off stack
        self.symbol_table.pop_environment()


    def visit_fun_def(self, fun_def):
        # Check parameters of function definition
        self.symbol_table.push_environment()
        # Check when return type is not void
        if fun_def.return_type.type_name.token_type != TokenType.VOID_TYPE:
            ret_type_name = fun_def.return_type.type_name.lexeme
            if (ret_type_name not in BASE_TYPES) and (ret_type_name not in list(self.structs.keys())):
                self.error('invalid return data type in function definition', fun_def.return_type.type_name)
        # Save the return statement of the function
        self.symbol_table.add("return", fun_def.return_type)
        # Check function parameters
        for var_def in fun_def.params:
            var_def.accept(self)
        # Check the body statements
        for stmt in fun_def.stmts:
            stmt.accept(self)
        # If all statements pass, pop environment
        self.symbol_table.pop_environment()

        
    def visit_return_stmt(self, return_stmt):
        # Update the curr_type with return statement expression
        return_stmt.expr.accept(self)
        # Get the function return type from symbol table
        return_type = self.symbol_table.get("return")
        # Compare expr curr_type with function defined return type (called in visit_return_stmt)
        if self.curr_type.type_name.token_type != TokenType.VOID_TYPE:
            if self.curr_type.type_name.token_type != return_type.type_name.token_type:
                self.error('expecting specific type return for function:', return_type.type_name)
        
            
    def visit_var_decl(self, var_decl):
        # Check for repeated variable names
        if self.symbol_table.exists_in_curr_env(var_decl.var_def.var_name.lexeme):
            self.error('variable declaration name already used', var_decl.var_def.var_name)
        else:
            # Check for valid data type
            var_type_name = var_decl.var_def.data_type.type_name.lexeme
            if (var_type_name not in BASE_TYPES) and (var_type_name not in list(self.structs.keys())):
                self.error('invalid variable declaration type', var_decl.var_def.data_type.type_name)
            # If passes tests add to symbol table
            self.symbol_table.add(var_decl.var_def.var_name.lexeme, var_decl.var_def.data_type)     
        # Check for expression type match
        if var_decl.expr != None:
            var_decl.expr.accept(self)
            var_type = var_decl.var_def.data_type
            # Check if expr is a null value
            if self.curr_type.type_name.token_type != TokenType.VOID_TYPE:
                # If not null, check for matching data types
                if self.curr_type.type_name.token_type != var_type.type_name.token_type: 
                    self.error('data types do not match for variable declaration', var_type.type_name)
                # Compare expr curr_type with function defined return type (called in visit_return_stmt)
                if self.curr_type.is_array != var_type.is_array:
                    self.error('is_array bool does not match for variable declaration data types', var_type.type_name)
        
        
    def visit_assign_stmt(self, assign_stmt):
        # Set current struct definition to None and last_array to false
        struct_def = None
        last_array = False

        # Check the lvalue path
        for var_ref in assign_stmt.lvalue:
            # If last reference was an array, throw error
            if last_array:
                self.error("cannot reference variable from array without expression", var_ref.var_name)
            # Check if variable exists in stack
            if not self.symbol_table.exists(var_ref.var_name.lexeme):
                # Variable must be a field
                if struct_def == None:
                    self.error('variable reference does not exist in stack', var_ref.var_name)
                if not self.get_field_type(struct_def, var_ref.var_name.lexeme):
                    self.error('variable reference does not exist in stack', var_ref.var_name) 
                else:
                    self.curr_type = self.get_field_type(struct_def, var_ref.var_name.lexeme)
            else:   
                # Set current type to the type referenced by var_name
                lhs_type = self.symbol_table.get(var_ref.var_name.lexeme)
                self.curr_type = DataType(lhs_type.is_array, lhs_type.is_list, lhs_type.type_name)

            # Check if array expression exists
            if var_ref.array_expr:
                # Get the expression and check
                var_ref.array_expr.accept(self)
                # Check if array expression produces an integer
                if self.curr_type.type_name.token_type != TokenType.INT_TYPE:
                    self.error("array expression is not of int type in var ref", self.curr_type.type_name)
                # Update curr_type with the data type accessed from array
                self.curr_type = DataType(False, None, lhs_type.type_name)

            # Check if current type is an ID, must be a struct
            if self.curr_type.type_name.token_type == TokenType.ID:
                struct_def = self.structs[self.curr_type.type_name.lexeme]
            # Set last type array value
            last_array = self.curr_type.is_array

        # Check that lvalue and expression are same type
        lhs_type = self.curr_type
        assign_stmt.expr.accept(self)
        if lhs_type.is_array != self.curr_type.is_array:
            self.error("lhs and rhs is_array bool of assignment statement do not match", self.curr_type.type_name)  
        if lhs_type.type_name.token_type != self.curr_type.type_name.token_type and self.curr_type.type_name.token_type != TokenType.VOID_TYPE:
            self.error("lhs and rhs data types of assignment statement do not match", self.curr_type.type_name) 


    def visit_while_stmt(self, while_stmt):
        # Push new environment
        self.symbol_table.push_environment()
        # Check conditional of while statement
        while_stmt.condition.accept(self)
        if self.curr_type.type_name.token_type != TokenType.BOOL_TYPE or self.curr_type.is_array == True:
            self.error("while conditional missing a boolean expression", self.curr_type.type_name)
        # Check statments within the loop
        for stmt in while_stmt.stmts:
            stmt.accept(self)
        # Pop environment
        self.symbol_table.pop_environment()

    
    def visit_list_fun_stmt(self, list_fun_stmt):
        # Set current struct definition to None and last_array to false
        struct_def = None
        last_array = False

        # Check the list path
        for var_ref in list_fun_stmt.list_path:
            # If last reference was an array, throw error
            if last_array:
                self.error("cannot reference variable from array without expression", var_ref.var_name)
            # Check if variable exists in stack
            if not self.symbol_table.exists(var_ref.var_name.lexeme):
                # Variable must be a field
                if struct_def == None:
                    self.error('variable reference does not exist in stack', var_ref.var_name)
                if not self.get_field_type(struct_def, var_ref.var_name.lexeme):
                    self.error('variable reference does not exist in stack', var_ref.var_name) 
                else:
                    self.curr_type = self.get_field_type(struct_def, var_ref.var_name.lexeme)
            else:   
                # Set current type to the type referenced by var_name
                lhs_type = self.symbol_table.get(var_ref.var_name.lexeme)
                self.curr_type = DataType(lhs_type.is_array, lhs_type.is_list, lhs_type.type_name)

            # Check if array expression exists
            if var_ref.array_expr:
                # Get the expression and check
                var_ref.array_expr.accept(self)
                # Check if array expression produces an integer
                if self.curr_type.type_name.token_type != TokenType.INT_TYPE:
                    self.error("array expression is not of int type in var ref", self.curr_type.type_name)
                # Update curr_type with the data type accessed from array
                self.curr_type = DataType(False, None, lhs_type.type_name)

            # Check if current type is an ID, must be a struct
            if self.curr_type.type_name.token_type == TokenType.ID:
                struct_def = self.structs[self.curr_type.type_name.lexeme]
            # Set last type array value
            last_array = self.curr_type.is_array

        # Check that list path is a list type
        if not self.curr_type.is_list:
            self.error("list function call must be on a declared list variable", self.curr_type.type_name) 
        
        # If the function is append, check append item matches list type
        if list_fun_stmt.function.token_type == TokenType.APPEND:
            lhs_type = self.curr_type
            list_fun_stmt.append_item.accept(self)
            if (lhs_type.type_name.token_type != self.curr_type.type_name.token_type) and (self.curr_type.type_name.token_type != TokenType.VOID_TYPE):
                self.error("lists must be homogeneous and must append a type that matches the rest of list", self.curr_type.type_name)


    def visit_for_stmt(self, for_stmt):
        # Push new environment
        self.symbol_table.push_environment()
        # Check Variable Declaration
        for_stmt.var_decl.accept(self)
        # Check conditional of for statement
        for_stmt.condition.accept(self)
        if self.curr_type.type_name.token_type != TokenType.BOOL_TYPE or self.curr_type.is_array == True:
            self.error("for conditional missing a boolean expression", self.curr_type.type_name)
        # Check assignment statement of for loop
        for_stmt.assign_stmt.accept(self)
        # Check statements within for loop
        for stmt in for_stmt.stmts:
            stmt.accept(self)
        # Pop environment
        self.symbol_table.pop_environment()
        
        
    def visit_if_stmt(self, if_stmt):
        # Push new environment
        self.symbol_table.push_environment()
        # If Part
        if_part = if_stmt.if_part
        # Verify condition
        if_part.condition.accept(self)
        if self.curr_type.type_name.token_type != TokenType.BOOL_TYPE or self.curr_type.is_array == True:
            self.error("if conditional missing a boolean expression", self.curr_type.type_name)
        # Verify statements
        for stmt in if_part.stmts:
            stmt.accept(self)       
        # Pop Environment
        self.symbol_table.pop_environment()

        # Else Ifs Part
        if if_stmt.else_ifs:
            for basic_if in if_stmt.else_ifs:  
                # Push new environment
                self.symbol_table.push_environment()  
                # Verify condition
                basic_if.condition.accept(self)
                if self.curr_type.type_name.token_type != TokenType.BOOL_TYPE or self.curr_type.is_array == True:
                    self.error("if conditional missing a boolean expression", self.curr_type.type_name)
                # Verify statements
                for stmt in basic_if.stmts:
                    stmt.accept(self)
                # Pop Environment
                self.symbol_table.pop_environment()

        # Push Environment
        self.symbol_table.push_environment()
        # Else Part
        if if_stmt.else_stmts:
            for stmt in if_stmt.else_stmts:
                stmt.accept(self)
        # Pop Environment
        self.symbol_table.pop_environment()
        
        
    def visit_call_expr(self, call_expr):
        # Check if function is a built in
        if call_expr.fun_name.lexeme in BUILT_INS:
            # Zero argument built ins
            if len(call_expr.args) == 0:
                # Print function
                if call_expr.fun_name.lexeme == 'print':
                    self.curr_type = DataType(False, None, Token(TokenType.VOID_TYPE, 'void', call_expr.fun_name.line, call_expr.fun_name.column))
                # Input function
                elif call_expr.fun_name.lexeme == 'input':
                    self.curr_type = DataType(False, None, Token(TokenType.STRING_TYPE, 'string', call_expr.fun_name.line, call_expr.fun_name.column))
                else:
                    self.error("invalid number of arguments entered for built in function", call_expr.fun_name)
            # One argument built ins
            elif len(call_expr.args) == 1:
                call_expr.args[0].accept(self)
                # Print function
                if call_expr.fun_name.lexeme == 'print':
                    valid_print_types = [TokenType.INT_TYPE, TokenType.DOUBLE_TYPE, TokenType.STRING_TYPE, TokenType.VOID_TYPE, TokenType.BOOL_TYPE]
                    if self.curr_type.type_name.token_type not in valid_print_types or self.curr_type.is_array == True:
                        self.error("invalid argument for print function", call_expr.fun_name)
                    self.curr_type = DataType(False, None, Token(TokenType.VOID_TYPE, 'void', call_expr.fun_name.line, call_expr.fun_name.column))
                # ITOS function
                elif call_expr.fun_name.lexeme == 'itos':
                    if self.curr_type.type_name.token_type != TokenType.INT_TYPE or self.curr_type.is_array == True:
                        self.error("invalid argument for itos function", call_expr.fun_name)
                    self.curr_type = DataType(False, None, Token(TokenType.STRING_TYPE, 'string', call_expr.fun_name.line, call_expr.fun_name.column))
                # DTOS function
                elif call_expr.fun_name.lexeme == 'dtos':
                    if self.curr_type.type_name.token_type != TokenType.DOUBLE_TYPE or self.curr_type.is_array == True:
                        self.error("invalid argument for dtos function", call_expr.fun_name)
                    self.curr_type = DataType(False, None, Token(TokenType.STRING_TYPE, 'string', call_expr.fun_name.line, call_expr.fun_name.column))
                # ITOD function
                elif call_expr.fun_name.lexeme == 'itod':
                    if self.curr_type.type_name.token_type != TokenType.INT_TYPE or self.curr_type.is_array == True:
                        self.error("invalid argument for itod function", call_expr.fun_name)
                    self.curr_type = DataType(False, None, Token(TokenType.DOUBLE_TYPE, 'string', call_expr.fun_name.line, call_expr.fun_name.column))
                # STOD function
                elif call_expr.fun_name.lexeme == 'stod':
                    if self.curr_type.type_name.token_type != TokenType.STRING_TYPE or self.curr_type.is_array == True:
                        self.error("invalid argument for itod function", call_expr.fun_name)
                    self.curr_type = DataType(False, None, Token(TokenType.DOUBLE_TYPE, 'string', call_expr.fun_name.line, call_expr.fun_name.column))
                # DTOI function
                elif call_expr.fun_name.lexeme == 'dtoi':
                    if self.curr_type.type_name.token_type != TokenType.DOUBLE_TYPE or self.curr_type.is_array == True:
                        self.error("invalid argument for dtoi function", call_expr.fun_name)
                    self.curr_type = DataType(False, None, Token(TokenType.INT_TYPE, 'string', call_expr.fun_name.line, call_expr.fun_name.column))
                # STOI function
                elif call_expr.fun_name.lexeme == 'stoi':
                    if self.curr_type.type_name.token_type != TokenType.STRING_TYPE or self.curr_type.is_array == True:
                        self.error("invalid argument for dtoi function", call_expr.fun_name)
                    self.curr_type = DataType(False, None, Token(TokenType.INT_TYPE, 'string', call_expr.fun_name.line, call_expr.fun_name.column))
                # Length function
                elif call_expr.fun_name.lexeme == 'length':
                    if self.curr_type.type_name.token_type != TokenType.STRING_TYPE and self.curr_type.is_array != True:
                        self.error("invalid argument for length function", call_expr.fun_name)
                    self.curr_type = DataType(False, None, Token(TokenType.INT_TYPE, 'string', call_expr.fun_name.line, call_expr.fun_name.column))
            # Two argument built in functions
            elif len(call_expr.args) == 2:
                # Get argument data types
                arg_types = []
                for arg in call_expr.args:
                    arg.accept(self)
                    if self.curr_type.is_array == True:
                        self.error("get arguments cannot be array", self.curr_type.type_name)
                    arg_types.append(self.curr_type)
                # GET function
                if call_expr.fun_name.lexeme == 'get':
                    if arg_types[0].type_name.token_type != TokenType.INT_TYPE or arg_types[1].type_name.token_type != TokenType.STRING_TYPE:
                        self.error("invalid argument for get function", call_expr.fun_name)
                    self.curr_type = DataType(False, None, Token(TokenType.STRING_TYPE, 'string', call_expr.fun_name.line, call_expr.fun_name.column))
                else:
                    self.error("invalid number of arguments entered for built in function", call_expr.fun_name)
            else:
                self.error("invalid number of arguments entered for built in function", call_expr.fun_name)

        # Check if function name exists in program
        elif call_expr.fun_name.lexeme in self.functions.keys():
            # Check number of arguments
            if len(call_expr.args) != len(self.functions[call_expr.fun_name.lexeme].params):
                self.error("invalid number of arguments in function call", call_expr.fun_name)
            # Check argument types
            fun_params = self.functions[call_expr.fun_name.lexeme].params
            for i in range(len(fun_params)):
                # Data Type
                call_expr.args[i].accept(self)
                token_type = self.curr_type.type_name.token_type
                if  token_type != fun_params[i].data_type.type_name.token_type and token_type != TokenType.VOID_TYPE:
                    self.error("incorrect data type for argument in function call", call_expr.fun_name)
                # Array
                if fun_params[i].data_type.is_array != self.curr_type.is_array:
                    self.error("incorrect array type for argument in function call", call_expr.fun_name)
            # Set current type as the function return type
            self.curr_type = self.functions[call_expr.fun_name.lexeme].return_type
        else:
            self.error("name for function call does not exist in program", call_expr.fun_name)
        

    def visit_expr(self, expr):
        # Check the first term
        expr.first.accept(self)
        # Record the LHS type
        lhs_type = self.curr_type

        # Check if there is more to current expression
        if expr.op != None:
            # Check the rest of expression
            expr.rest.accept(self)
            # Record the rhs type
            rhs_type = self.curr_type

            # Check whether the expression operator is relational or math
            relation_ops = [TokenType.LESS, TokenType.LESS_EQ, TokenType.GREATER, TokenType.GREATER_EQ]
            compare_ops = [TokenType.EQUAL, TokenType.NOT_EQUAL]
            combine_ops = [TokenType.AND, TokenType.OR]
            math_ops = [TokenType.PLUS, TokenType.MINUS, TokenType.TIMES, TokenType.DIVIDE]

            # INT Type Case
            if lhs_type.type_name.token_type == TokenType.INT_TYPE:
                # Math Case
                if expr.op.token_type in math_ops:
                    if rhs_type.type_name.token_type != TokenType.INT_TYPE:
                        self.error('lhs and rhs data types do not match in expression', lhs_type.type_name)
                    self.curr_type = lhs_type
                # Compare Case
                elif expr.op.token_type in compare_ops:
                    if rhs_type.type_name.token_type != TokenType.INT_TYPE and rhs_type.type_name.token_type != TokenType.VOID_TYPE:
                        self.error('lhs and rhs data types do not match in expression', lhs_type.type_name)
                    self.curr_type = DataType(False, None, Token(TokenType.BOOL_TYPE, 'bool', lhs_type.type_name.line, lhs_type.type_name.column))
                # Relational Case
                elif expr.op.token_type in relation_ops:
                    if rhs_type.type_name.token_type != TokenType.INT_TYPE:
                        self.error('lhs and rhs data types do not match in expression', lhs_type.type_name)
                    self.curr_type = DataType(False, None, Token(TokenType.BOOL_TYPE, 'bool', lhs_type.type_name.line, lhs_type.type_name.column))
                else:
                    self.error('invalid expression operation for int type', lhs_type.type_name)
                    
            # DOUBLE Type Case
            if lhs_type.type_name.token_type == TokenType.DOUBLE_TYPE:
                # Math Case
                if expr.op.token_type in math_ops:
                    if rhs_type.type_name.token_type != TokenType.DOUBLE_TYPE:
                        self.error('lhs and rhs data types do not match in expression', lhs_type.type_name)
                    self.curr_type = lhs_type
                # Compare Case
                elif expr.op.token_type in compare_ops:
                    if rhs_type.type_name.token_type != TokenType.DOUBLE_TYPE and rhs_type.type_name.token_type != TokenType.VOID_TYPE:
                        self.error('lhs and rhs data types do not match in expression', lhs_type.type_name)
                    self.curr_type = DataType(False, None, Token(TokenType.BOOL_TYPE, 'bool', lhs_type.type_name.line, lhs_type.type_name.column))
                # Relational Case
                elif expr.op.token_type in relation_ops:
                    if rhs_type.type_name.token_type != TokenType.DOUBLE_TYPE:
                        self.error('lhs and rhs data types do not match in expression', lhs_type.type_name)
                    self.curr_type = DataType(False, None, Token(TokenType.BOOL_TYPE, 'bool', lhs_type.type_name.line, lhs_type.type_name.column))
                else:
                    self.error('invalid expression operation for double type', lhs_type.type_name)
                    
            # STRING Type Case
            if lhs_type.type_name.token_type == TokenType.STRING_TYPE:
                # Math Case
                if expr.op.token_type == TokenType.PLUS:
                    if rhs_type.type_name.token_type != TokenType.STRING_TYPE:
                        self.error('lhs and rhs data types do not match in expression', lhs_type.type_name)
                    self.curr_type = lhs_type
                # Compare Case
                elif expr.op.token_type in compare_ops:
                    if rhs_type.type_name.token_type != TokenType.STRING_TYPE and rhs_type.type_name.token_type != TokenType.VOID_TYPE:
                        self.error('lhs and rhs data types do not match in expression', lhs_type.type_name)
                    self.curr_type = DataType(False, None, Token(TokenType.BOOL_TYPE, 'bool', lhs_type.type_name.line, lhs_type.type_name.column))
                # Relational Case
                elif expr.op.token_type in relation_ops:
                    if rhs_type.type_name.token_type != TokenType.STRING_TYPE:
                        self.error('lhs and rhs data types do not match in expression', lhs_type.type_name)
                    self.curr_type = DataType(False, None, Token(TokenType.BOOL_TYPE, 'bool', lhs_type.type_name.line, lhs_type.type_name.column))
                else:
                    self.error('invalid expression operation for string type', lhs_type.type_name)
                    
            # BOOL Type Case
            if lhs_type.type_name.token_type == TokenType.BOOL_TYPE:
                # Compare Case
                if expr.op.token_type in compare_ops:
                    if rhs_type.type_name.token_type != TokenType.BOOL_TYPE and rhs_type.type_name.token_type != TokenType.VOID_TYPE:
                        self.error('lhs and rhs data types do not match in expression', lhs_type.type_name)
                    self.curr_type = DataType(False, None, Token(TokenType.BOOL_TYPE, 'bool', lhs_type.type_name.line, lhs_type.type_name.column))
                elif expr.op.token_type in combine_ops:
                    if rhs_type.type_name.token_type != TokenType.BOOL_TYPE:
                        self.error('lhs and rhs data types do not match in expression', lhs_type.type_name)
                    self.curr_type = DataType(False, None, Token(TokenType.BOOL_TYPE, 'bool', lhs_type.type_name.line, lhs_type.type_name.column))
                else:
                    self.error('invalid expression operation for bool type', lhs_type.type_name)
            
            # VOID Type Case
            if lhs_type.type_name.token_type == TokenType.VOID_TYPE:
                # Compare case only valid place, automatically becomes boolean if true
                if expr.op.token_type not in compare_ops and expr.op.token_type not in combine_ops:
                    self.error("null expression terms can only be compared with == or !=", lhs_type.type_name)
                self.curr_type = DataType(False, None, Token(TokenType.BOOL_TYPE, 'bool', lhs_type.type_name.line, lhs_type.type_name.column))
            
            # STRUCT Type Case
            if lhs_type.type_name.token_type == TokenType.ID:
                # Compare case only valid place, automatically becomes boolean if true
                if expr.op.token_type not in compare_ops:
                    self.error("struct expression terms can only be compared with == or !=", lhs_type.type_name)
                self.curr_type = DataType(False, None, Token(TokenType.BOOL_TYPE, 'bool', lhs_type.type_name.line, lhs_type.type_name.column))

        # Check not_op ensures a bool type
        if expr.not_op:
            # Check if curr_type is also a bool'
            if self.curr_type.type_name.token_type != TokenType.BOOL_TYPE:
                self.error('not boolean paired with invalid expression type', self.curr_type.type_name)
   

    def visit_data_type(self, data_type):
        # note: allowing void (bad cases of void caught by parser)
        name = data_type.type_name.lexeme
        if name == 'void' or name in BASE_TYPES or name in self.structs:
            self.curr_type = data_type
        else: 
            self.error(f'invalid type "{name}"', data_type.type_name)
            
    
    def visit_var_def(self, var_def):
        # Check for repeated variable names
        if self.symbol_table.exists_in_curr_env(var_def.var_name.lexeme):
            self.error('variable definition name already used', var_def.var_name)
        else:
            # Check for valid data type
            var_type_name = var_def.data_type.type_name.lexeme
            if (var_type_name not in BASE_TYPES) and (var_type_name not in list(self.structs.keys())):
                self.error('invalid variable type in variable definition:', var_def.data_type.type_name)
            self.curr_type = var_def.data_type
            # If passes tests add to symbol table
            self.symbol_table.add(var_def.var_name.lexeme, var_def.data_type)

        
    def visit_simple_term(self, simple_term):
        # Pass visitor into rvalue of simple term
        simple_term.rvalue.accept(self)
        
    
    def visit_complex_term(self, complex_term):
        # Pass visitor in to expr of complex term
        complex_term.expr.accept(self)
        

    def visit_simple_rvalue(self, simple_rvalue):
        value = simple_rvalue.value
        line = simple_rvalue.value.line
        column = simple_rvalue.value.column
        type_token = None 
        if value.token_type == TokenType.INT_VAL:
            type_token = Token(TokenType.INT_TYPE, 'int', line, column)
        elif value.token_type == TokenType.DOUBLE_VAL:
            type_token = Token(TokenType.DOUBLE_TYPE, 'double', line, column)
        elif value.token_type == TokenType.STRING_VAL:
            type_token = Token(TokenType.STRING_TYPE, 'string', line, column)
        elif value.token_type == TokenType.BOOL_VAL:
            type_token = Token(TokenType.BOOL_TYPE, 'bool', line, column)
        elif value.token_type == TokenType.NULL_VAL:
            type_token = Token(TokenType.VOID_TYPE, 'void', line, column)
        self.curr_type = DataType(False, None, type_token)

        
    def visit_new_rvalue(self, new_rvalue):
        # Declare is_array checker to update curr_type
        is_array = False
        # Check if it is an array case
        if new_rvalue.array_expr != None:
            is_array = True
            new_rvalue.array_expr.accept(self)
            if self.curr_type.type_name.token_type != TokenType.INT_TYPE:
                self.error("array expression must be an integer value", self.curr_type.type_name)
        # Check if it is a struct case
        if new_rvalue.struct_params != None:
            # Get struct definition from dictionary
            struct_def = self.structs[new_rvalue.type_name.lexeme]
            # Check that struct argument lengths match
            if len(struct_def.fields) != len(new_rvalue.struct_params):
                self.error("invalid argument count for struct creation", new_rvalue.type_name)
            # Check argument types
            str_params = struct_def.fields
            for i in range(len(str_params)):
                # Data Type
                new_rvalue.struct_params[i].accept(self)
                token_type = self.curr_type.type_name.token_type
                if  token_type != str_params[i].data_type.type_name.token_type and token_type != TokenType.VOID_TYPE:
                    self.error("incorrect data type for argument in struct creation", new_rvalue.type_name)
                # Array
                if str_params[i].data_type.is_array != self.curr_type.is_array and token_type != TokenType.VOID_TYPE:
                    self.error("incorrect array type for argument in struct creation", new_rvalue.type_name) 
        # Update curr_type
        self.curr_type = DataType(is_array, None, new_rvalue.type_name)
        
    
    def visit_list_rvalue(self, list_rvalue):
        # Set current struct definition to None and last_array to false
        struct_def = None
        last_array = False

        # Check the list path
        for var_ref in list_rvalue.list_path:
            # If last reference was an array, throw error
            if last_array:
                self.error("cannot reference variable from array without expression", var_ref.var_name)
            # Check if variable exists in stack
            if not self.symbol_table.exists(var_ref.var_name.lexeme):
                # Variable must be a field
                if struct_def == None:
                    self.error('variable reference does not exist in stack', var_ref.var_name)
                if not self.get_field_type(struct_def, var_ref.var_name.lexeme):
                    self.error('variable reference does not exist in stack', var_ref.var_name) 
                else:
                    self.curr_type = self.get_field_type(struct_def, var_ref.var_name.lexeme)
            else:   
                # Set current type to the type referenced by var_name
                lhs_type = self.symbol_table.get(var_ref.var_name.lexeme)
                self.curr_type = DataType(lhs_type.is_array, lhs_type.is_list, lhs_type.type_name)

            # Check if array expression exists
            if var_ref.array_expr:
                # Get the expression and check
                var_ref.array_expr.accept(self)
                # Check if array expression produces an integer
                if self.curr_type.type_name.token_type != TokenType.INT_TYPE:
                    self.error("array expression is not of int type in var ref", self.curr_type.type_name)
                # Update curr_type with the data type accessed from array
                self.curr_type = DataType(False, None, lhs_type.type_name)

            # Check if current type is an ID, must be a struct
            if self.curr_type.type_name.token_type == TokenType.ID:
                struct_def = self.structs[self.curr_type.type_name.lexeme]
            # Set last type array value
            last_array = self.curr_type.is_array

        # Check that list path is a list type
        if not self.curr_type.is_list:
            self.error("list function call must be on a declared list variable", self.curr_type.type_name) 
        
        # Check that the list type is one of doubles, ints, or strings for max/min function
        if self.curr_type.type_name.token_type not in [TokenType.DOUBLE_TYPE, TokenType.INT_TYPE]:
            self.error("lists must be homogeneous and must append a type that matches the rest of list", self.curr_type.type_name)
        else:
            self.curr_type = DataType(False, False, self.curr_type.type_name)

            
    def visit_var_rvalue(self, var_rvalue):
        # Set current struct_definition to None and last referenced is_array to false
        struct_def = None
        last_array = False

        # Check each of the variable references in path
        for var_ref in var_rvalue.path:
            # If last reference was an array, throw error
            if last_array:
                self.error("cannot reference variable from array without expression", var_ref.var_name)

            # Check if variable exists in stack
            if not self.symbol_table.exists(var_ref.var_name.lexeme):
                if struct_def == None:
                    self.error('variable reference does not exist in stack', var_ref.var_name)
                if not self.get_field_type(struct_def, var_ref.var_name.lexeme):
                    self.error('variable reference does not exist in stack', var_ref.var_name) 
                else:
                    self.curr_type = self.get_field_type(struct_def, var_ref.var_name.lexeme)
            else:   
                # Set current type to the type referenced by var_name
                lhs_type = self.symbol_table.get(var_ref.var_name.lexeme)
                self.curr_type = DataType(lhs_type.is_array, lhs_type.is_list, lhs_type.type_name)

            # Check if array expression exists
            if var_ref.array_expr:
                # Get the expression and check
                var_ref.array_expr.accept(self)
                # Check if array expression produces an integer
                if self.curr_type.type_name.token_type != TokenType.INT_TYPE:
                    self.error("array expression is not of int type in var ref", self.curr_type.type_name)
                # Update curr_type with the data type accessed from array
                self.curr_type = DataType(False, None, lhs_type.type_name)

            # Check if current type is an ID, must be a struct
            if self.curr_type.type_name.token_type == TokenType.ID:
                struct_def = self.structs[self.curr_type.type_name.lexeme]
            # Set last type array value
            last_array = self.curr_type.is_array
