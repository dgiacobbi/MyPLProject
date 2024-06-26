"""Print Visitor for pretty printing a MyPL program.

NAME: David Giacobbi
DATE: Spring 2024
CLASS: CPSC 326

"""

from dataclasses import dataclass
from mypl_token import Token, TokenType
from mypl_ast import *


class PrintVisitor(Visitor):
    """Visitor implementation to pretty print MyPL program."""

    def __init__(self):
        self.indent = 0

    # Helper Functions
        
    def output(self, msg):
        """Prints message without ending newline.

        Args:
           msg -- The string to print.

        """
        print(msg, end='')

        
    def output_indent(self):
        """Prints an initial indent string."""
        self.output('  ' * self.indent)


    def output_semicolon(self, stmt):
        """Prints a semicolon if the type of statment should end in a
        semicolon.
        
        Args:
            stmt -- The statement to print a semicolon after.

        """
        if type(stmt) in [VarDecl, AssignStmt, ReturnStmt, CallExpr]:
            self.output(';')

    # Visitor Functions
    
    def visit_program(self, program):
        for struct in program.struct_defs:
            struct.accept(self)
            self.output('\n')
        for fun in program.fun_defs:
            fun.accept(self)
            self.output('\n')            

            
    def visit_struct_def(self, struct_def):
        self.output('struct ' + struct_def.struct_name.lexeme + ' {\n')
        self.indent += 1
        for var_def in struct_def.fields:
            self.output_indent()
            var_def.accept(self)
            self.output(';\n')
        self.indent -= 1
        self.output('}\n')


    def visit_fun_def(self, fun_def):
        fun_def.return_type.accept(self)
        self.output(' ' + fun_def.fun_name.lexeme + '(')
        for i in range(len(fun_def.params)):
            fun_def.params[i].accept(self)
            if i < len(fun_def.params) - 1:
                self.output(', ')
        self.output(') {\n')
        self.indent += 1
        for stmt in fun_def.stmts:
            self.output_indent()
            stmt.accept(self)
            self.output_semicolon(stmt)
            self.output('\n')
        self.indent -= 1
        self.output('}\n')


    def visit_var_decl(self, var_decl):
        # Print data type, name pair
        var_decl.var_def.accept(self)
        self.output(' ')
        # If assignment exists, add expression
        if not var_decl.expr == None:
            self.output('= ')
            var_decl.expr.accept(self)


    def visit_var_def(self, var_def):
        # Print data type and corresponding name
        var_def.data_type.accept(self)
        self.output(' ' + var_def.var_name.lexeme)


    def visit_data_type(self, data_type):
        # Check if definition includes array and print if true
        if data_type.is_array == True:
            self.output('array ')
        # Print variable type name
        self.output(data_type.type_name.lexeme)
    

    def visit_for_stmt(self, for_stmt):
        self.output('for (')
        # Variable declaration
        for_stmt.var_decl.accept(self)
        self.output(';')
        # Conditional statement
        for_stmt.condition.accept(self)
        self.output(';')
        # Assignment statement
        for_stmt.assign_stmt.accept(self)
        self.output(') {\n')
        self.indent += 1
        # Statements
        for i in range(len(for_stmt.stmts)):
            self.output_indent()
            for_stmt.stmts[i].accept(self)
            self.output_semicolon(for_stmt.stmts[i])
            self.output('\n')
        # End loop
        self.indent -= 1
        self.output_indent()
        self.output('}\n')

    
    def visit_if_stmt(self, if_stmt):
        # First if statement
        self.output('if (')
        basic_if = if_stmt.if_part
        # Add condition
        basic_if.condition.accept(self) 
        self.output(') {\n')
        # Add statements
        self.indent += 1
        for i in range(len(basic_if.stmts)):
            self.output_indent()
            basic_if.stmts[i].accept(self)
            self.output_semicolon(basic_if.stmts[i])
            self.output('\n')
        self.indent -= 1
        self.output_indent()
        self.output('}')

        # Else if statement
        if not if_stmt.else_ifs == []:
            for i in range(len(if_stmt.else_ifs)):
                self.output('\n')
                self.output_indent()
                self.output('elseif (')
                basic_if = if_stmt.else_ifs[i]
                # Add condition
                basic_if.condition.accept(self) 
                self.output(') {\n')
                # Add statements
                self.indent += 1
                for i in range(len(basic_if.stmts)):
                    self.output_indent()
                    basic_if.stmts[i].accept(self)
                    self.output_semicolon(basic_if.stmts[i])
                    self.output('\n')
                self.indent -= 1
                self.output_indent()
                self.output('}')

        # Else statement
        if not if_stmt.else_stmts == []:
            self.output('\n')
            self.output_indent()
            self.output('else {\n')
            self.indent += 1
            for i in range(len(if_stmt.else_stmts)):
                self.output_indent()
                if_stmt.else_stmts[i].accept(self)
                self.output_semicolon(if_stmt.else_stmts[i])
                self.output('\n')
            self.indent -= 1
            self.output_indent()
            self.output('}')    
    

    def visit_assign_stmt(self, assign_stmt):
        # Lvalue path for assignment
        for i in range(len(assign_stmt.lvalue)):
            var_ref = assign_stmt.lvalue[i]
            # Variable name
            self.output(var_ref.var_name.lexeme)
            # Array condition
            if not var_ref.array_expr == None:
                self.output('[')
                var_ref.array_expr.accept(self)
                self.output(']')
            if i != len(assign_stmt.lvalue) - 1:
                self.output('.')
        # Assignment operator
        self.output(' = ')
        # Right side expression
        assign_stmt.expr.accept(self)


    def visit_return_stmt(self, return_stmt):
        # Return syntax
        self.output('return ')
        # Print expression
        return_stmt.expr.accept(self)
    

    def visit_while_stmt(self, while_stmt):
        # While condition
        self.output('while (')
        while_stmt.condition.accept(self)
        self.output(') {\n')
        # While statments
        self.indent += 1
        for i in range(len(while_stmt.stmts)):
            self.output_indent()
            while_stmt.stmts[i].accept(self)
            self.output_semicolon(while_stmt.stmts[i])
            self.output('\n')
        self.indent -= 1
        # Closing syntax
        self.output_indent()
        self.output('}')

    
    def visit_call_expr(self, call_expr):
        # Function name
        self.output(call_expr.fun_name.lexeme + '(')
        # Arguments
        for i in range(len(call_expr.args)):
            call_expr.args[i].accept(self)
            if i != len(call_expr.args) - 1:
                self.output(', ')
        self.output(')')

    
    def visit_expr(self, expr):
        # Not operator
        if expr.not_op == True:
            self.output('not (')
        # First expression term
        expr.first.accept(self)
        # Operator
        if not expr.op == None:
            self.output(' ' + expr.op.lexeme + ' ')
        # Rest of expression
        if not expr.rest == None:
            expr.rest.accept(self)
        # Not closed
        if expr.not_op == True:
            self.output(')')
    

    def visit_complex_term(self, complex_term):
        self.output('(')
        complex_term.expr.accept(self)
        self.output(')')


    def visit_simple_term(self, simple_term):
        simple_term.rvalue.accept(self)
    

    def visit_new_rvalue(self, new_rvalue):
        # New syntax and type name
        self.output('new ' + new_rvalue.type_name.lexeme)
        # Array condition
        if not new_rvalue.array_expr == None:
            self.output('[')
            new_rvalue.array_expr.accept(self)
            self.output(']')
        # Struct params condition
        if not new_rvalue.struct_params == None:
            self.output('(')
            for i in range(len(new_rvalue.struct_params)):
                new_rvalue.struct_params[i].accept(self)
                if i != len(new_rvalue.struct_params) - 1:
                    self.output(', ')
            self.output(')')


    def visit_var_rvalue(self, var_rvalue):
        # Create path
        for i in range(len(var_rvalue.path)):
            var_ref = var_rvalue.path[i]
            # Variable name
            self.output(var_ref.var_name.lexeme)
            # Array condition
            if not var_ref.array_expr == None:
                self.output('[')
                var_ref.array_expr.accept(self)
                self.output(']')
            if i != len(var_rvalue.path) - 1:
                self.output('.')


    def visit_var_ref(self, var_ref):
        # Variable name
        self.output(var_ref.var_name.lexeme)
        # Array condition
        if not var_ref.array_expr == None:
            self.output('[')
            var_ref.array_expr.accept(self)
            self.output(']')
    

    def visit_simple_rvalue(self, simple_rvalue):
        if simple_rvalue.value.token_type == TokenType.STRING_VAL:
            self.output('"' + simple_rvalue.value.lexeme + '"')
        else:
            self.output(simple_rvalue.value.lexeme)