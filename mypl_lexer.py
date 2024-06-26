"""The MyPL Lexer class.

NAME: David Giacobbi
DATE: Spring 2024
CLASS: CPSC 326

"""

from mypl_token import *
from mypl_error import *


class Lexer:
    """For obtaining a token stream from a program."""

    def __init__(self, in_stream):
        """Create a Lexer over the given input stream.

        Args:
            in_stream -- The input stream. 

        """
        self.in_stream = in_stream
        self.line = 1
        self.column = 0


    def read(self):
        """Returns and removes one character from the input stream."""
        self.column += 1
        return self.in_stream.read_char()

    
    def peek(self):
        """Returns but doesn't remove one character from the input stream."""
        return self.in_stream.peek_char()

    
    def eof(self, ch):
        """Return true if end-of-file character"""
        return ch == ''

    
    def error(self, message, line, column):
        raise LexerError(f'{message} at line {line}, column {column}')

    
    def next_token(self):
        """Return the next token in the lexer's input stream."""
        # Read initial character
        ch = self.read()

        # Read all whitespace
        if ch.isspace():
            # If new line increase line count
            if ch == '\n':
                self.line += 1
                self.column = 0
            # Call for next token
            return self.next_token()

        # Check for EOF (End of File Check)
        if self.eof(ch):
            return Token(TokenType.EOS, '', self.line, self.column)

        # Arithmentic Operators (Single Character Check)
        if ch == '+':
            return Token(TokenType.PLUS, "+", self.line, self.column)
        if ch == '-':
            return Token(TokenType.MINUS, "-", self.line, self.column)
        if ch == '*':
            return Token(TokenType.TIMES, "*", self.line, self.column)

        # Punctuation (Single Character Check)
        if ch == '.':
            return Token(TokenType.DOT, ".", self.line, self.column)
        if ch == ',':
            return Token(TokenType.COMMA, ",", self.line, self.column)
        if ch == '(':
            return Token(TokenType.LPAREN, "(", self.line, self.column)
        if ch == ')':
            return Token(TokenType.RPAREN, ")", self.line, self.column)
        if ch == '[':
            return Token(TokenType.LBRACKET, "[", self.line, self.column)
        if ch == ']':
            return Token(TokenType.RBRACKET, "]", self.line, self.column)
        if ch == '{':
            return Token(TokenType.LBRACE, "{", self.line, self.column)
        if ch == '}':
            return Token(TokenType.RBRACE, "}", self.line, self.column)
        if ch == ';':
            return Token(TokenType.SEMICOLON, ";", self.line, self.column)

        # <= Relational Check (2+ Character Check)
        if ch == '<':
            column_start = self.column
            if self.peek() == '=':
                self.read()
                return Token(TokenType.LESS_EQ, "<=", self.line, column_start)
            else:
                return Token(TokenType.LESS, "<", self.line, column_start)

        # >= Relational Check (2+ Character Check)  
        if ch == '>':
            column_start = self.column
            if self.peek() == '=':
                self.read()
                return Token(TokenType.GREATER_EQ, ">=", self.line, column_start)
            else:
                return Token(TokenType.GREATER, ">", self.line, column_start)

        # != Relational Check (2+ Character Check)    
        if ch == '!':
            column_start = self.column
            if self.peek() == '=':
                self.read()
                return Token(TokenType.NOT_EQUAL, "!=", self.line, column_start)
            else:
                return self.error("! not a valid character", self.line, column_start)
            
        # == Relational Check (2+ Character Check)
        if ch == '=':
            column_start = self.column
            if self.peek() == '=':
                self.read()
                return Token(TokenType.EQUAL, "==", self.line, column_start)
            else:
                return Token(TokenType.ASSIGN, "=", self.line, column_start)
        
        # Comments Check (2+ Character Check)
        if ch == '/':
            # Track column for token start
            column_start = self.column

            # Check for Comment Indicator //
            if self.peek() == '/':
                # Read the next / and peek next character for end of comment 
                self.read()
                next_char = self.peek() 
                comment_lexeme = ""
                # Loop and add to lexeme until end of comment is reached
                while(next_char != '\n' and next_char != ''):
                    next_char = self.read() 
                    comment_lexeme += next_char 
                    next_char = self.peek()               
                # Return Comment Token
                return Token(TokenType.COMMENT, comment_lexeme, self.line, column_start)
            
            # Return Divide Token if comment not found
            else:
                return Token(TokenType.DIVIDE, "/", self.line, column_start)

        # Check for string values
        if ch == '"':
            # Peek the next char and track column count for string
            next_char = self.peek()
            column_start = self.column

            # Check if next char results in unclosed string
            if next_char == '\n' or next_char == '':
                return self.error("Missing closed quotation", self.line, column_start)

            # While loop to build lexeme unless EOF is found before end of quotation
            string_val = ""
            while(next_char != '"'):
                # Read next character and append lexeme with last checked character before peeking
                self.read()
                string_val += next_char
                next_char = self.peek()
                # Check if next char results in unclosed string
                if next_char == '\n' or next_char == '':
                    return self.error("Missing closed quotation", self.line, column_start)
            
            # All string value tests passed, return token and read closed quotation
            self.read()
            return Token(TokenType.STRING_VAL, string_val, self.line, column_start)
            
        # Check for integer and double values
        if ch.isdecimal():
            # Save column start and peek next character
            column_start = self.column
            next_char = self.peek()

            # Check leading zero error
            if ch == '0' and next_char.isdecimal():
                return self.error("No leading zeros are allowed", self.line, column_start)
            
            # Check for valid integer value
            int_val = "" + ch
            while(next_char.isdecimal() == True or next_char == '.'):

                # Check for double value
                if next_char == '.':
                    self.read()
                    double_val = int_val + "."
                    next_char = self.peek()
                    # Make sure double is valid
                    if not next_char.isdecimal():
                        return self.error("Double must have digits following decimal", self.line, column_start)
                    # Loop and add to lexeme until end of double is reached
                    while(next_char.isdecimal() == True):
                        self.read()
                        double_val += next_char 
                        next_char = self.peek()
                    return Token(TokenType.DOUBLE_VAL, double_val, self.line, column_start)

                # Loop through digits, checking for double each time
                self.read()
                int_val += next_char 
                next_char = self.peek()
            
            # Return integer token if no doubles were found
            return Token(TokenType.INT_VAL, int_val, self.line, column_start)

        # Check for reserved words and identifiers
        if ch.isalpha():
            # Save column start
            column_start = self.column

            # Loop and add to lexeme until whitespace is found for the identifier or reserved words
            lexeme = "" + ch
            next_char = self.peek()
            while(next_char.isalpha() or next_char.isdecimal() or next_char == '_'):
                self.read()
                lexeme += next_char 
                next_char = self.peek()

            # Check if lexeme matches with any of the comparator values or null
            if lexeme == "true":
                return Token(TokenType.BOOL_VAL, lexeme, self.line, column_start)
            if lexeme == "false":
                return Token(TokenType.BOOL_VAL, lexeme, self.line, column_start)
            if lexeme == "and":
                return Token(TokenType.AND, lexeme, self.line, column_start)
            if lexeme == "or":
                return Token(TokenType.OR, lexeme, self.line, column_start)
            if lexeme == "not":
                return Token(TokenType.NOT, lexeme, self.line, column_start)
            if lexeme == "null":
                return Token(TokenType.NULL_VAL, lexeme, self.line, column_start)
                
            # Check if lexeme matches with any of the primitive data types
            if lexeme == "int":
                return Token(TokenType.INT_TYPE, lexeme, self.line, column_start)
            if lexeme == "double":
                return Token(TokenType.DOUBLE_TYPE, lexeme, self.line, column_start)
            if lexeme == "string":
                return Token(TokenType.STRING_TYPE, lexeme, self.line, column_start)
            if lexeme == "bool":
                return Token(TokenType.BOOL_TYPE, lexeme, self.line, column_start)
            if lexeme == "void":
                return Token(TokenType.VOID_TYPE, lexeme, self.line, column_start)
            
            # Check if lexeme matches with any of the reserved words
            if lexeme == "struct":
                return Token(TokenType.STRUCT, lexeme, self.line, column_start)
            if lexeme == "array":
                return Token(TokenType.ARRAY, lexeme, self.line, column_start)
            if lexeme == "for":
                return Token(TokenType.FOR, lexeme, self.line, column_start)
            if lexeme == "while":
                return Token(TokenType.WHILE, lexeme, self.line, column_start)
            if lexeme == "if":
                return Token(TokenType.IF, lexeme, self.line, column_start)
            if lexeme == "elseif":
                return Token(TokenType.ELSEIF, lexeme, self.line, column_start)
            if lexeme == "else":
                return Token(TokenType.ELSE, lexeme, self.line, column_start)
            if lexeme == "new":
                return Token(TokenType.NEW, lexeme, self.line, column_start)
            if lexeme == "return":
                return Token(TokenType.RETURN, lexeme, self.line, column_start)
            
            # CHECK IF LEXEME IS PART OF LIST PROJECT TOKENS
            if lexeme == "list":
                return Token(TokenType.LIST, lexeme, self.line, column_start)
            if lexeme == "append":
                return Token(TokenType.APPEND, lexeme, self.line, column_start)
            if lexeme == "clear":
                return Token(TokenType.CLEAR, lexeme, self.line, column_start)
            if lexeme == "pop":
                return Token(TokenType.POP, lexeme, self.line, column_start)
            if lexeme == "max":
                return Token(TokenType.MAX, lexeme, self.line, column_start)
            if lexeme == "min":
                return Token(TokenType.MIN, lexeme, self.line, column_start)
            
            
            # If lexeme fails all reserved word tests, return identifier token
            return Token(TokenType.ID, lexeme, self.line, column_start)
        
        # Any other input is invalid and must have an error message
        return self.error("Invalid Symbol", self.line, self.column)