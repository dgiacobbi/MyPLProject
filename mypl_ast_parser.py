"""MyPL AST parser implementation.

NAME: David Giacobbi
DATE: Spring 2024
CLASS: CPSC 326
"""

from mypl_error import *
from mypl_token import *
from mypl_lexer import *
from mypl_ast import *


class ASTParser:

    def __init__(self, lexer):
        """Create a MyPL syntax checker (parser). 
        
        Args:
            lexer -- The lexer to use in the parser.

        """
        self.lexer = lexer
        self.curr_token = None

        
    def parse(self):
        """Start the parser, returning a Program AST node."""
        program_node = Program([], [])
        self.advance()
        while not self.match(TokenType.EOS):
            if self.match(TokenType.STRUCT):
                self.struct_def(program_node)
            else:
                self.fun_def(program_node)
        self.eat(TokenType.EOS, 'expecting EOF')
        return program_node

        
    #----------------------------------------------------------------------
    # Helper functions
    #----------------------------------------------------------------------

    def error(self, message):
        """Raises a formatted parser error.

        Args:
            message -- The basic message (expectation)

        """
        lexeme = self.curr_token.lexeme
        line = self.curr_token.line
        column = self.curr_token.column
        err_msg = f'{message} found "{lexeme}" at line {line}, column {column}'
        raise ParserError(err_msg)


    def advance(self):
        """Moves to the next token of the lexer."""
        self.curr_token = self.lexer.next_token()
        # skip comments
        while self.match(TokenType.COMMENT):
            self.curr_token = self.lexer.next_token()

            
    def match(self, token_type):
        """True if the current token type matches the given one.

        Args:
            token_type -- The token type to match on.

        """
        return self.curr_token.token_type == token_type

    
    def match_any(self, token_types):
        """True if current token type matches on of the given ones.

        Args:
            token_types -- Collection of token types to check against.

        """
        for token_type in token_types:
            if self.match(token_type):
                return True
        return False

    
    def eat(self, token_type, message):
        """Advances to next token if current tokey type matches given one,
        otherwise produces and error with the given message.

        Args: 
            token_type -- The totken type to match on.
            message -- Error message if types don't match.

        """
        if not self.match(token_type):
            self.error(message)
        self.advance()

        
    def is_bin_op(self):
        """Returns true if the current token is a binary operator."""
        ts = [TokenType.PLUS, TokenType.MINUS, TokenType.TIMES, TokenType.DIVIDE,
              TokenType.AND, TokenType.OR, TokenType.EQUAL, TokenType.LESS,
              TokenType.GREATER, TokenType.LESS_EQ, TokenType.GREATER_EQ,
              TokenType.NOT_EQUAL]
        return self.match_any(ts)
    


    #----------------------------------------------------------------------
    # Recursive descent functions
    #----------------------------------------------------------------------

    def struct_def(self, program_node):
        """Check for well-formed struct definition."""
        # Create a struct node to initialize struct
        struct_node = StructDef(None, [])
        self.eat(TokenType.STRUCT, "expecting STRUCT token in struct definition")

        # Name the struct using ID
        struct_node.struct_name = self.curr_token
        self.eat(TokenType.ID, "expecting ID token in struct definition")

        # Fill the struct with fields, passing in the struct node
        self.eat(TokenType.LBRACE, "expecting LBRACE token in struct definition")
        # Check the fields within a struct if any exist
        if not self.match(TokenType.RBRACE):
            self.fields(struct_node)
        self.eat(TokenType.RBRACE, "expecting RBRACE token in struct definition")

        # Append filled out struct to the program struct list
        program_node.struct_defs.append(struct_node)

        
    def fields(self, struct_node):
        """Check for well-formed struct fields."""
        # Read data type declarations until the right brace is found
        while not self.match(TokenType.RBRACE):
            # Create new variable definition and identify variable's data_type
            field = VarDef(None, None)
            field.data_type = self.data_type()
            # Assign name to current field and verify semicolon
            field.var_name = self.curr_token
            self.eat(TokenType.ID, "expecting ID token in fields")
            self.eat(TokenType.SEMICOLON, "expecting SEMICOLON token in fields")
            # Append field VarDef to list of VarDefs for struct node
            struct_node.fields.append(field)


    def fun_def(self, program_node):
        """Check for well-formed function definition."""
        # Create a new FunDef node with empty parameters
        fun_def_node = FunDef(None, None, [], [])

        # Check the return feature of the function
        if not self.match(TokenType.VOID_TYPE):
            fun_def_node.return_type = self.data_type()
        else:
            fun_def_node.return_type = DataType(False, False, self.curr_token)
            self.advance()

        # Fill out function name
        fun_def_node.fun_name = self.curr_token
        self.eat(TokenType.ID, "expecting ID toke in function definition")

        # Check for parameters and append to params list of VarDefs
        self.eat(TokenType.LPAREN, "expecting LPAREN token in function definition")
        if not self.match(TokenType.RPAREN):
            self.params(fun_def_node)
        self.eat(TokenType.RPAREN, "expecting RPAREN token in function definition")
        self.eat(TokenType.LBRACE, "expecting LBRACE token in function definition")

        # Check for statements until the right brace is found
        while not self.match(TokenType.RBRACE):
            fun_def_node.stmts.append(self.stmt())
        self.advance()

        # Append completed FunDef to program node
        program_node.fun_defs.append(fun_def_node)


    def params(self, fun_def_node):
        """Check for well-formed function formal parameters."""
        # Create a new parameter VarDef
        param_var_def = VarDef(None, None)
        # Check for valid data type ID pair and append VarDef node to fun_def node
        param_var_def.data_type = self.data_type()
        param_var_def.var_name = self.curr_token
        fun_def_node.params.append(param_var_def)
        self.eat(TokenType.ID, "expecting ID token in parameters")
        # While more parameters exist via commas, continue to check type ID pairs
        while self.match(TokenType.COMMA):
            self.advance()
            #Create a new VarDef, fill out parameters
            param_var_def = VarDef(None, None)
            param_var_def.data_type = self.data_type()
            param_var_def.var_name = self.curr_token
            self.eat(TokenType.ID, "expecting ID token in parameters")
            # Append parameter to params list in FunDef
            fun_def_node.params.append(param_var_def)


    def data_type(self):
        """Check for well-formed data types."""
        # Create empty DataType Node to fill from VarDef
        data_type_node = DataType(None, None, None)
        # Check for struct
        if self.match(TokenType.ID):
            data_type_node.is_array = False
            data_type_node.type_name = self.curr_token
            self.advance()
        # Check for valid array type declaration
        elif self.match(TokenType.ARRAY):
            data_type_node.is_array = True
            self.advance()
            if self.match(TokenType.ID):
                data_type_node.type_name = self.curr_token
                self.advance()
            else:
                self.base_type(data_type_node)

        # Check for valid list type declaration
        elif self.match(TokenType.LIST):
            data_type_node.is_list = True
            # Assumins same traits as an array
            data_type_node.is_array = True
            self.advance()
            if self.match(TokenType.ID):
                data_type_node.type_name = self.curr_token
                self.advance()
            else:
                self.base_type(data_type_node)

        # Check for base types
        else:
            data_type_node.is_array = False
            self.base_type(data_type_node)
        # Return filled out data type node
        return data_type_node


    def base_type(self, data_type_node):
        """Check for well-formed base types."""
        # Verify the base types with match_any, throwing error if none are found
        base_type_list = [TokenType.INT_TYPE, TokenType.DOUBLE_TYPE, TokenType.BOOL_TYPE, TokenType.STRING_TYPE]
        if not self.match_any(base_type_list):
            self.error("expecting base type token")
        else:
            data_type_node.type_name = self.curr_token
            self.advance()


    def stmt(self):
        """Check for well-formed statements. Return a statement node."""
        # Check for loop and conditional statements
        if self.match(TokenType.WHILE):
            stmt_node = self.while_stmt()
        elif self.match(TokenType.IF):
            stmt_node = self.if_stmt()
        elif self.match(TokenType.FOR):
            stmt_node = self.for_stmt()
        # Check for return statement
        elif self.match(TokenType.RETURN):
            stmt_node = self.ret_stmt()
            self.eat(TokenType.SEMICOLON, "expecting SEMICOLON token in statement")
        # Check for assignment statment and call expressions
        elif self.match(TokenType.ID):
            # Save ID token and move past ID token and check further
            id_token = self.curr_token
            self.advance()
            # Note: ID already consumed for these functions
            if self.match(TokenType.LPAREN):
                # Fill out call_expr node and then update fun_name with id_token
                stmt_node = self.call_expr(id_token)
            # Check for possible struct declaration case
            elif self.match(TokenType.ID):
                # Part of variable declaration (Special Case), create a VarDecl node
                stmt_node = VarDecl(None, None)
                # Use saved tokens to create struct VarDef node
                stmt_node.var_def = VarDef(DataType(False, None, id_token), self.curr_token)
                self.advance()
                # Check for an assign token, if so check for expression following
                if self.match(TokenType.ASSIGN):
                    self.advance()
                    # Create an expression node
                    stmt_node.expr = Expr(False, None, None, None)
                    self.expr(stmt_node.expr)
            else:

                # # Save the lvalue from the lvalue recursive call
                curr_lvalue = self.lvalue(id_token)
                # Check if current token is an assign, otherwise list function
                if self.curr_token.token_type == TokenType.ASSIGN:
                    # Create assign statement node and pass lvalue from call
                    stmt_node = self.assign_stmt(curr_lvalue)
                else:
                    # Create a list function node and pass lvalue from call
                    stmt_node = self.list_fun_stmt(curr_lvalue)


            self.eat(TokenType.SEMICOLON, "expecting SEMICOLON token in statement")
        # Check for variable declaration statement
        else:
            # Fill out VarDecl node, EXCEPT variable name of VarDef within node
            stmt_node = self.vdecl_stmt()
            self.eat(TokenType.SEMICOLON, "expecting SEMICOLON token in statement")
        # Return the filled out statement node of specific type
        return stmt_node


    def vdecl_stmt(self):
        """Check for well-formed variable declaration statements."""
        # Create a new VarDecl node
        var_decl_node = VarDecl(VarDef(None, None), None)
        # Check for valid data type
        var_decl_node.var_def.data_type = self.data_type()
        var_decl_node.var_def.var_name = self.curr_token
        self.eat(TokenType.ID, "expecting ID token in variable declaration statement")
        # Check for an assign token, if so check for expression following
        if self.match(TokenType.ASSIGN):
            self.advance()
            # Create an expression node
            var_decl_node.expr = Expr(False, None, None, None)
            self.expr(var_decl_node.expr)
        # Return filled out VarDecl node
        return var_decl_node


    def assign_stmt(self, curr_lvalue):
        """Check for well-formed assignment statements."""
        # Check for valid left value followed by assignment and expression
        # Note: ID token already consumed for beginning of this function

        # Create an AssignStmt node
        assign_stmt_node = AssignStmt([], None)
        # Pass in first ID token for lvalue
        assign_stmt_node.lvalue = curr_lvalue
        self.eat(TokenType.ASSIGN, "expecting ASSIGN token in assignment statement")

        # Create an expression node
        assign_stmt_node.expr = Expr(False, None, None, None)
        self.expr(assign_stmt_node.expr)
        # Return assignment statement node
        return assign_stmt_node
    


    def list_fun_stmt(self, curr_lvalue):
        """Check for well-formed list function statements."""
        # Create an empty list function node
        list_fun_node = ListFunStmt(None, None, None)

        # Cases for the rest of the statement
        fun_name = curr_lvalue[-1].var_name
        if fun_name.token_type == TokenType.APPEND:
            self.eat(TokenType.LPAREN, "expecting LPAREN in list function statement")
            list_fun_node.append_item = Expr(None, None, None, None)
            self.expr(list_fun_node.append_item)
            self.eat(TokenType.RPAREN, "expecting RPAREN in list function statment")
        elif fun_name.token_type == TokenType.CLEAR:
            self.eat(TokenType.LPAREN, "expecting LPAREN in list function statement")
            self.eat(TokenType.RPAREN, "expecting RPAREN in list function statment")
        elif fun_name.token_type == TokenType.POP:
            self.eat(TokenType.LPAREN, "expecting LPAREN in list function statement")
            self.eat(TokenType.RPAREN, "expecting RPAREN in list function statment")
        else:
            self.error("improper list params in list function statement")
        list_fun_node.function = curr_lvalue[-1].var_name

        # Create the variable path to the referenced list
        list_path = curr_lvalue[0:len(curr_lvalue)-1]
        list_fun_node.list_path = list_path

        # Return created statement node
        return list_fun_node



    def lvalue(self, first_id_token):
        """Check for well-formed lvalue."""
        # ID already eaten from statement, do not eat again
        # Create an empty list to fill with VarRef nodes
        var_ref_list = []
        # Create a VarRef node for first ID token
        var_ref_node = VarRef(first_id_token, None)
        # Check for bracketed expression or empty case
        if self.match(TokenType.LBRACKET):
            self.advance()
            # Create an expression node
            var_ref_node.array_expr = Expr(False, None, None, None)
            self.expr(var_ref_node.array_expr)
            self.eat(TokenType.RBRACKET, "expecting RBRACKET token in left value")
        # Append filled out first VarRef to list
        var_ref_list.append(var_ref_node)

        # Check if a list function is within the path
        list_fun_check = False

        # Check continuations of left value in loop
        while self.match(TokenType.DOT):
            self.advance()
            # Check if list function was already eaten
            if list_fun_check:
                self.error("list function call inside path expression")
            # Create new node and fill out
            var_ref_node = VarRef(self.curr_token, None)
            # Check list condition
            if self.match_any([TokenType.APPEND, TokenType.CLEAR, TokenType.POP]):
                self.eat(self.curr_token.token_type, "expecting a LIST FUNCTION in lvalue")
                list_fun_check = True
            else:
                self.eat(TokenType.ID, "expecting ID token in left value")
                # Check for bracketed expression if exists
                if self.match(TokenType.LBRACKET):
                    self.advance()
                    # Create an expression node
                    var_ref_node.array_expr = Expr(False, None, None, None)
                    self.expr(var_ref_node.array_expr)
                    self.eat(TokenType.RBRACKET, "expecting RBRACKET token in left value")
            # Append filled out node to VarRef list
            var_ref_list.append(var_ref_node)

        # Return a list fun path
        return var_ref_list


    def if_stmt(self):
        """Check for well-formed if statement."""
        # Create an IfStmt Node to fill
        if_stmt_node = IfStmt(None, [], [])
        self.eat(TokenType.IF, "expecting IF token in if statement")
        self.eat(TokenType.LPAREN, "expecting LPAREN token in if statement")
        # Boolean expression check for conditional, create BasicIf node
        basic_if_node = BasicIf(None, [])
        # Create an expression node
        basic_if_node.condition = Expr(False, None, None, None)
        self.expr(basic_if_node.condition)
        self.eat(TokenType.RPAREN, "expecting RPAREN token in if statement")
        self.eat(TokenType.LBRACE, "expecting LBRACE token in if statement")
        # Only if statments exist, verify until right brace found and advance
        while not self.match(TokenType.RBRACE):
            basic_if_node.stmts.append(self.stmt())
        self.advance()
        # Append the basic if statement to if statment node
        if_stmt_node.if_part = basic_if_node
        # Check the tail in different function
        self.if_stmt_t(if_stmt_node)
        # Return filled out IfStmt node
        return if_stmt_node


    def if_stmt_t(self, if_stmt_node):
        """Check for well-formed if statement tail."""
        # Check the else if parameter
        if self.match(TokenType.ELSEIF):
            # Create a new BasicIf node
            basic_if_node = BasicIf(None, [])
            self.advance()
            self.eat(TokenType.LPAREN, "expecting LPAREN token in if statement tail")
            # else if boolean expression check
            # Create an expression node
            basic_if_node.condition = Expr(False, None, None, None)
            self.expr(basic_if_node.condition)
            self.eat(TokenType.RPAREN, "expecting RPAREN token in if statement tail")
            self.eat(TokenType.LBRACE, "expecting LBRACE token in if statement tail")
            # Verify statments until right brace is found and advance
            while not self.match(TokenType.RBRACE):
                basic_if_node.stmts.append(self.stmt())
            self.advance()
            # Append filled node to else_ifs list
            if_stmt_node.else_ifs.append(basic_if_node)
            # Recursive call to tail to check for more else if or else
            self.if_stmt_t(if_stmt_node)
        # Check the else parameter
        elif self.match(TokenType.ELSE):
            self.advance()
            self.eat(TokenType.LBRACE, "expecting LBRACE token in if statement tail")
            # Verify statements until right brace is found and advance
            while not self.match(TokenType.RBRACE):
                # Append new statements to else statement list
                if_stmt_node.else_stmts.append(self.stmt())
            self.advance()


    def while_stmt(self):
        """Check for well-formed while statement."""
        # Create a WhileStmt node
        while_stmt_node = WhileStmt(None, [])
        self.eat(TokenType.WHILE, "expecting WHILE token in while statment")
        self.eat(TokenType.LPAREN, "expecting LPAREN token in while statement")
        # Boolean expression check
        # Create an expression node
        while_stmt_node.condition = Expr(False, None, None, None)
        self.expr(while_stmt_node.condition)
        self.eat(TokenType.RPAREN, "expecting RPAREN token in while statement")
        self.eat(TokenType.LBRACE, "expecting LBRACE token in while statement")
        # Only if statment occurs check otherwise read right brace
        while not self.match(TokenType.RBRACE):
            while_stmt_node.stmts.append(self.stmt())
        self.advance()
        # Return filled out WhileStmt node
        return while_stmt_node


    def for_stmt(self):
        """Check for well-formed for statement."""
        # Create an empty ForStmt node
        for_stmt_node = ForStmt(None, None, None, [])
        self.eat(TokenType.FOR, "expecting FOR token in for loop statement")
        self.eat(TokenType.LPAREN, "expecting LPAREN token in for loop statement")
        # Variable initialized, assign var_decl the VarDecl node returned by function
        for_stmt_node.var_decl = self.vdecl_stmt()
        self.eat(TokenType.SEMICOLON, "expecting SEMICOLON token in for loop statement")
        # Boolean expression
        # Create an expression node
        for_stmt_node.condition = Expr(False, None, None, None)
        self.expr(for_stmt_node.condition)
        self.eat(TokenType.SEMICOLON, "expecting SEMICOLON token in for loop statement")
        # Eat ID part of assignment statement, then check the rest of increment parameter
        first_id_token = self.curr_token
        self.eat(TokenType.ID, "expecting ID token in for loop statement")
        # Pass eaten ID token into assign statement function
        curr_lvalue = self.lvalue(first_id_token)
        for_stmt_node.assign_stmt = self.assign_stmt(curr_lvalue)
        self.eat(TokenType.RPAREN, "expecting RPAREN token in for loop statement")
        self.eat(TokenType.LBRACE, "expecting LBRACE token in for loop statement")
        # Check for verified statements until the right brace is found and advance
        while not self.match(TokenType.RBRACE):
            for_stmt_node.stmts.append(self.stmt())
        self.advance()
        # Return filled out ForStmt node
        return for_stmt_node


    def call_expr(self, first_id_token):
        """Check for well-formed call expression."""
        # Create a CallExpr node
        call_expr_node = CallExpr(first_id_token, [])
        # Note: ID already read, so start with eating LPAREN
        self.eat(TokenType.LPAREN, "expecting LPAREN token in call expression")
        # Check for right parenthesis for the empty string case
        if not self.match(TokenType.RPAREN):
            # Append individual argument expressions to call expression arg list
            # Create an expression node
            expr_node = Expr(False, None, None, None)
            self.expr(expr_node)
            call_expr_node.args.append(expr_node)
            # Check for Kleene star case of (COMMA <expr>)
            while self.match(TokenType.COMMA):
                self.advance()
                # Append individual argument expressions to call expression arg list
                # Create an expression node
                expr_node = Expr(False, None, None, None)
                self.expr(expr_node)
                call_expr_node.args.append(expr_node)
        # Advance past right parenthesis
        self.advance()
        # Return filled out call expression node
        return call_expr_node


    def ret_stmt(self):
        """Check for well-formed return statement."""
        # Create a return statement node
        ret_node = ReturnStmt(None)
        # Verify expression follows the return reserved token
        self.eat(TokenType.RETURN, "expecting RETURN token in return statement")
        # Create an expression node
        ret_node.expr = Expr(False, None, None, None)
        self.expr(ret_node.expr)
        # Return filled out return statement node
        return ret_node


    def expr(self, expr_node):
        """Check for well-formed expressions."""
        # NOT <expr> case
        if self.match(TokenType.NOT):
            expr_node.not_op = True
            self.advance()
            self.expr(expr_node)
        # LPAREN <expr> RPAREN case
        elif self.match(TokenType.LPAREN):
            self.advance()
            # Create an ExprTerm Node
            expr_term = ComplexTerm(Expr(False, None, None, None))
            self.expr(expr_term.expr)
            expr_node.first = expr_term
            self.eat(TokenType.RPAREN, "expecting RPAREN token in expression")
        # <rvalue> case
        else:
            # Create an ExprTerm Node
            expr_term = SimpleTerm(self.rvalue())
            expr_node.first = expr_term
        # Second part of expression rule, check for <bin_op> <expr> or empty case
        if self.is_bin_op():
            expr_node.op = self.curr_token
            self.advance()
            expr_node.rest = Expr(False, None, None, None)
            self.expr(expr_node.rest)


    def bin_op(self):
        """Check for well-formed binary operations."""
        # Check for a binary operator, otherwise return error
        if not self.is_bin_op():
            self.error("expecting binary operation token")


    def rvalue(self):
        """Check for well-formed rvalue."""
        # New rvalue case, starts with new
        if self.match(TokenType.NEW):
            rvalue_node = self.new_rvalue()
        # NULL_VAL token case
        elif self.match(TokenType.NULL_VAL):
            rvalue_node = SimpleRValue(self.curr_token)
            self.eat(TokenType.NULL_VAL, "expecting NULL_VAL token in right value")
        # Determine whether to choose call expression or right value variable
        elif self.match(TokenType.ID):
            # Track first_id_token to develop node in other functions
            first_id_token = self.curr_token
            self.advance()
            # Move past ID token and check next token in stream
            if self.match(TokenType.LPAREN):
                rvalue_node = self.call_expr(first_id_token)
            else:
            
                # Save the rvalue from the rvalue recursive call
                curr_rvalue = self.var_rvalue(first_id_token)
                # Check if last token in path is a list function, otherwise
                if curr_rvalue.path[-1].var_name.token_type in [TokenType.MAX, TokenType.MIN]:
                    # Create rvalue node and pass path to create list_rvalue node
                    rvalue_node = self.list_rvalue(curr_rvalue.path)
                else:
                    # Regular var r value set
                    rvalue_node = curr_rvalue

        # Check for valid base value if none exist
        else:
            rvalue_node = self.base_rvalue()
        # Return whichever RValue type has been found
        return rvalue_node
    


    def list_rvalue(self, path):
        """Check for well-formed list rvalue (max or min)."""
        # Create an empty list function node
        list_rvalue_node = ListRValue(None, None)

        # Set the function name
        list_rvalue_node.fun_name = path[-1].var_name
        # Create the variable path to the referenced list
        list_path = path[0:len(path)-1]
        list_rvalue_node.list_path = list_path
        
        # Ensure the rest of the list call is well-typed
        self.eat(TokenType.LPAREN, "expecting LPAREN token at the end of list rvalue call")
        self.eat(TokenType.RPAREN, "expecting RPAREN token at the end of list rvalue call")
        
        # Return created rvalue node
        return list_rvalue_node



    def new_rvalue(self):
        """Check for well-formed new rvalue."""
        # Create a NewRValue node
        new_rvalue_node = NewRValue(None, None, None)
        # Check for new token in either case
        self.eat(TokenType.NEW, "expecting NEW token in new right value in new right value")
        # Check for base type case where ID does not exist
        if not self.match(TokenType.ID):
            self.base_type(new_rvalue_node)
        else:
            # Advance ID if found
            new_rvalue_node.type_name = self.curr_token
            self.advance()
        # Check for LPAREN, implying the first case of rule
        if self.match(TokenType.LPAREN):
            self.advance()
            new_rvalue_node.struct_params = []
            # Check for list of comma spaced expressions
            while not self.match(TokenType.RPAREN):
                # Create an expression node
                expr_node = Expr(False, None, None, None)
                self.expr(expr_node)
                new_rvalue_node.struct_params.append(expr_node)
                while self.match(TokenType.COMMA):
                    self.advance()
                    # Create an expression node
                    expr_node = Expr(False, None, None, None)
                    self.expr(expr_node)
                    new_rvalue_node.struct_params.append(expr_node)
            # Advance the right parenthesis
            self.advance()
        # Case two of the rule is implied then
        else:
            self.eat(TokenType.LBRACKET, "expecting LBRACKET token in new right value")
            # Create an expression node
            new_rvalue_node.array_expr = Expr(False, None, None, None)
            self.expr(new_rvalue_node.array_expr)
            self.eat(TokenType.RBRACKET, "expecting RBRACKET token in new right value")
        # Return filled new r_value node
        return new_rvalue_node


    def base_rvalue(self):
        """Check for well-formed base rvalue."""
        base_rvalue_list = [TokenType.INT_VAL, TokenType.DOUBLE_VAL, TokenType.BOOL_VAL, TokenType.STRING_VAL]
        # Check for valid base, if true advance
        if not self.match_any(base_rvalue_list):
            self.error("expecting a valid base rvalue token")
        else:
            # Create a SimpleRValue node with current token
            base_node = SimpleRValue(self.curr_token)
            self.advance()
        return base_node


    def var_rvalue(self, first_id_token):
        """Check for well-formed variable rvalue."""
        # Create new VarRValue node
        var_rvalue_node = VarRValue([])
        # Create a VarRef node for the first id token
        var_ref_node = VarRef(first_id_token, None)
        # Note: ID already eaten in right value function, so check for left bracket
        if self.match(TokenType.LBRACKET):
            self.advance()
            # Create an expression node
            var_ref_node.array_expr = Expr(False, None, None, None)
            self.expr(var_ref_node.array_expr)
            self.eat(TokenType.RBRACKET, "expecting RBRACKET token in right value variable")
        # Append VarRef from first ID to path list
        var_rvalue_node.path.append(var_ref_node)

        # List function check for path expression
        list_fun_check = False

        # Check Kleene Star of second part of rule (DOT ID (LBRACKET <expr> RBRACKET | empty))
        while self.match(TokenType.DOT):
            self.advance()
            # Check if list function is already part of path
            if list_fun_check:
                self.error("list function inside path expression, not at the end")
            # Create a VarRef node for the first id token
            var_ref_node = VarRef(self.curr_token, None)
            if self.curr_token.token_type in [TokenType.MAX, TokenType.MIN]:
                self.eat(self.curr_token.token_type, "expecting list expression function")
                list_fun_check = True
            else:
                self.eat(TokenType.ID, "expecting ID token in right value variable")
                # Check for empty case of additional expression case
                if self.match(TokenType.LBRACKET):
                    self.advance()
                    # Create an expression node
                    var_ref_node.array_expr = Expr(False, None, None, None)
                    self.expr(var_ref_node.array_expr)
                    self.eat(TokenType.RBRACKET, "expecting RBRACKET in right bracket variable")
            # Append VarRef from first ID to path list
            var_rvalue_node.path.append(var_ref_node)
        # Return filled VarRValue node
        return var_rvalue_node
    