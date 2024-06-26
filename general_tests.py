"""Unit testing from the previous homeworks to ensure that
implementation is not breaking successful compiler.

NAME: S. Bowers and D. Giacobbi
DATE: Spring 2024
CLASS: CPSC 326

"""

import pytest
import io

from mypl_error import *
from mypl_iowrapper import *
from mypl_token import *
from mypl_lexer import *
from mypl_ast_parser import *
from mypl_semantic_checker import *
from mypl_symbol_table import *
from mypl_opcode import *
from mypl_frame import *
from mypl_vm import *
from mypl_var_table import *
from mypl_code_gen import *

#----------------------------------------------------------------------
# LEXER TEST CASES
#----------------------------------------------------------------------

def test_simple_symbol():
    in_stream = FileWrapper(io.StringIO('.'))
    l = Lexer(in_stream)
    t = l.next_token()
    assert t.token_type == TokenType.DOT
    assert t.lexeme == '.'
    assert t.line == 1
    assert t.column == 1

    
def test_empty_input():
    in_stream = FileWrapper(io.StringIO(''))
    l = Lexer(in_stream)
    t = l.next_token()
    assert t.token_type == TokenType.EOS
    assert t.lexeme == ''
    assert t.line == 1
    assert t.column == 1

    
def test_symbol_then_eof():
    in_stream = FileWrapper(io.StringIO(';'))
    l = Lexer(in_stream)
    t = l.next_token()
    assert t.token_type == TokenType.SEMICOLON
    assert t.lexeme == ';'
    assert t.line == 1
    assert t.column == 1
    t = l.next_token()
    assert t.token_type == TokenType.EOS
    assert t.lexeme == ''
    assert t.line == 1
    assert t.column == 2

    
def test_single_comment():
    in_stream = FileWrapper(io.StringIO('// a comment'))
    l = Lexer(in_stream)
    t = l.next_token()
    assert t.token_type == TokenType.COMMENT
    assert t.lexeme == ' a comment'
    assert t.line == 1
    assert t.column == 1

    
def test_two_comments():
    m = ('// first comment\n'
         ' // second comment')
    in_stream = FileWrapper(io.StringIO(m))
    l = Lexer(in_stream)
    t = l.next_token()
    assert t.token_type == TokenType.COMMENT
    assert t.lexeme == ' first comment'
    assert t.line == 1
    assert t.column == 1
    t = l.next_token()
    assert t.token_type == TokenType.COMMENT
    assert t.lexeme == ' second comment'
    assert t.line == 2
    assert t.column == 2

    
def test_one_character_symbols():
    in_stream = FileWrapper(io.StringIO(',.;+-*/()[]{}=<>'))
    l = Lexer(in_stream)
    types = [TokenType.COMMA, TokenType.DOT, TokenType.SEMICOLON, TokenType.PLUS,
             TokenType.MINUS, TokenType.TIMES, TokenType.DIVIDE, TokenType.LPAREN,
             TokenType.RPAREN, TokenType.LBRACKET, TokenType.RBRACKET,
             TokenType.LBRACE, TokenType.RBRACE, TokenType.ASSIGN,
             TokenType.LESS, TokenType.GREATER]
    for i in range(len(types)):
        t = l.next_token()
        assert t.token_type == types[i]
        assert t.line == 1
        assert t.column == i + 1
    assert l.next_token().token_type == TokenType.EOS


def test_two_character_symbols():
    in_stream = FileWrapper(io.StringIO('!=>=<==='))
    l = Lexer(in_stream)
    types = [TokenType.NOT_EQUAL, TokenType.GREATER_EQ, TokenType.LESS_EQ,
             TokenType.EQUAL]
    for i in range(len(types)):
        t = l.next_token()
        assert t.token_type == types[i]
        assert t.line == 1
        assert t.column == (i * 2) + 1
    assert l.next_token().token_type == TokenType.EOS


def test_one_symbol_per_line():
    in_stream = FileWrapper(io.StringIO(',\n.\n;\n('))    
    l = Lexer(in_stream)
    t = l.next_token()
    assert t.token_type == TokenType.COMMA
    assert t.lexeme == ','
    assert t.line == 1
    assert t.column == 1
    t = l.next_token()
    assert t.token_type == TokenType.DOT
    assert t.lexeme == '.'
    assert t.line == 2
    assert t.column == 1
    t = l.next_token()
    assert t.token_type == TokenType.SEMICOLON
    assert t.lexeme == ';'
    assert t.line == 3
    assert t.column == 1
    t = l.next_token()
    assert t.token_type == TokenType.LPAREN
    assert t.lexeme == '('
    assert t.line == 4
    assert t.column == 1
    assert l.next_token().token_type == TokenType.EOS


def test_one_char_strings():
    in_stream = FileWrapper(io.StringIO('"a" "?" "<"'))
    l = Lexer(in_stream)
    t = l.next_token()
    assert t.token_type == TokenType.STRING_VAL
    assert t.lexeme == 'a'
    assert t.line == 1
    assert t.column == 1
    t = l.next_token()
    assert t.token_type == TokenType.STRING_VAL
    assert t.lexeme == '?'
    assert t.line == 1
    assert t.column == 5
    t = l.next_token()
    assert t.token_type == TokenType.STRING_VAL
    assert t.lexeme == '<'
    assert t.line == 1
    assert t.column == 9
    assert l.next_token().token_type == TokenType.EOS


def test_multi_char_strings():
    in_stream = FileWrapper(io.StringIO('"abc" "><!=" "foo bar baz"'))
    l = Lexer(in_stream)
    t = l.next_token()
    assert t.token_type == TokenType.STRING_VAL
    assert t.lexeme == 'abc'
    assert t.line == 1
    assert t.column == 1
    t = l.next_token()
    assert t.token_type == TokenType.STRING_VAL
    assert t.lexeme == '><!='
    assert t.line == 1
    assert t.column == 7
    t = l.next_token()
    assert t.token_type == TokenType.STRING_VAL
    assert t.lexeme == 'foo bar baz'
    assert t.line == 1
    assert t.column == 14
    assert l.next_token().token_type == TokenType.EOS


def test_basic_ints():
    in_stream = FileWrapper(io.StringIO('0 42 10 9876543210'))
    l = Lexer(in_stream)
    t = l.next_token()
    assert t.token_type == TokenType.INT_VAL
    assert t.lexeme == '0'
    assert t.line == 1
    assert t.column == 1
    t = l.next_token()
    assert t.token_type == TokenType.INT_VAL
    assert t.lexeme == '42'
    assert t.line == 1
    assert t.column == 3
    t = l.next_token()
    assert t.token_type == TokenType.INT_VAL
    assert t.lexeme == '10'
    assert t.line == 1
    assert t.column == 6
    t = l.next_token()
    assert t.token_type == TokenType.INT_VAL
    assert t.lexeme == '9876543210'
    assert t.line == 1
    assert t.column == 9
    assert l.next_token().token_type == TokenType.EOS


def test_basic_doubles():
    in_stream = FileWrapper(io.StringIO('0.0 0.00 3.14 321.123'))
    l = Lexer(in_stream)
    t = l.next_token()
    assert t.token_type == TokenType.DOUBLE_VAL
    assert t.lexeme == '0.0'
    assert t.line == 1
    assert t.column == 1
    t = l.next_token()
    assert t.token_type == TokenType.DOUBLE_VAL
    assert t.lexeme == '0.00'
    assert t.line == 1
    assert t.column == 5
    t = l.next_token()
    assert t.token_type == TokenType.DOUBLE_VAL
    assert t.lexeme == '3.14'
    assert t.line == 1
    assert t.column == 10
    t = l.next_token()
    assert t.token_type == TokenType.DOUBLE_VAL
    assert t.lexeme == '321.123'
    assert t.line == 1
    assert t.column == 15
    assert l.next_token().token_type == TokenType.EOS

    
def test_special_values():
    in_stream = FileWrapper(io.StringIO('null true false'))
    l = Lexer(in_stream)
    t = l.next_token()
    assert t.token_type == TokenType.NULL_VAL
    assert t.lexeme == 'null'
    assert t.line == 1
    assert t.column == 1
    t = l.next_token()
    assert t.token_type == TokenType.BOOL_VAL
    assert t.lexeme == 'true'
    assert t.line == 1
    assert t.column == 6
    t = l.next_token()    
    assert t.token_type == TokenType.BOOL_VAL
    assert t.lexeme == 'false'
    assert t.line == 1
    assert t.column == 11
    assert l.next_token().token_type == TokenType.EOS    

    
def test_primitive_types():
    in_stream = FileWrapper(io.StringIO('int double string bool void'))
    l = Lexer(in_stream)
    t = l.next_token()
    assert t.token_type == TokenType.INT_TYPE
    assert t.lexeme == 'int'
    assert t.line == 1
    assert t.column == 1
    t = l.next_token()
    assert t.token_type == TokenType.DOUBLE_TYPE
    assert t.lexeme == 'double'
    assert t.line == 1
    assert t.column == 5
    t = l.next_token()    
    assert t.token_type == TokenType.STRING_TYPE
    assert t.lexeme == 'string'
    assert t.line == 1
    assert t.column == 12
    t = l.next_token()    
    assert t.token_type == TokenType.BOOL_TYPE
    assert t.lexeme == 'bool'
    assert t.line == 1
    assert t.column == 19
    t = l.next_token()    
    assert t.token_type == TokenType.VOID_TYPE
    assert t.lexeme == 'void'
    assert t.line == 1
    assert t.column == 24
    assert l.next_token().token_type == TokenType.EOS    

    
def test_logical_operators():
    in_stream = FileWrapper(io.StringIO('and or not'))
    l = Lexer(in_stream)
    t = l.next_token()
    assert t.token_type == TokenType.AND
    assert t.lexeme == 'and'
    assert t.line == 1
    assert t.column == 1
    t = l.next_token()
    assert t.token_type == TokenType.OR
    assert t.lexeme == 'or'
    assert t.line == 1
    assert t.column == 5
    t = l.next_token()
    assert t.token_type == TokenType.NOT
    assert t.lexeme == 'not'
    assert t.line == 1
    assert t.column == 8
    assert l.next_token().token_type == TokenType.EOS    


def test_if_statement_reserved_words():
    in_stream = FileWrapper(io.StringIO('if elseif else'))
    l = Lexer(in_stream)
    t = l.next_token()
    assert t.token_type == TokenType.IF
    assert t.lexeme == 'if'
    assert t.line == 1
    assert t.column == 1
    t = l.next_token()
    assert t.token_type == TokenType.ELSEIF
    assert t.lexeme == 'elseif'
    assert t.line == 1
    assert t.column == 4
    t = l.next_token()
    assert t.token_type == TokenType.ELSE
    assert t.lexeme == 'else'
    assert t.line == 1
    assert t.column == 11
    assert l.next_token().token_type == TokenType.EOS    


def test_loop_statement_reserved_words():
    in_stream = FileWrapper(io.StringIO('while for'))
    l = Lexer(in_stream)
    t = l.next_token()
    assert t.token_type == TokenType.WHILE
    assert t.lexeme == 'while'
    assert t.line == 1
    assert t.column == 1
    t = l.next_token()
    assert t.token_type == TokenType.FOR
    assert t.lexeme == 'for'
    assert t.line == 1
    assert t.column == 7
    assert l.next_token().token_type == TokenType.EOS    

    
def test_function_and_complex_type_reserved_words():
    in_stream = FileWrapper(io.StringIO('return struct array new'))
    l = Lexer(in_stream)
    t = l.next_token()
    assert t.token_type == TokenType.RETURN
    assert t.lexeme == 'return'
    assert t.line == 1
    assert t.column == 1
    t = l.next_token()
    assert t.token_type == TokenType.STRUCT
    assert t.lexeme == 'struct'
    assert t.line == 1
    assert t.column == 8
    t = l.next_token()
    assert t.token_type == TokenType.ARRAY
    assert t.lexeme == 'array'
    assert t.line == 1
    assert t.column == 15
    t = l.next_token()
    assert t.token_type == TokenType.NEW
    assert t.lexeme == 'new'
    assert t.line == 1
    assert t.column == 21
    assert l.next_token().token_type == TokenType.EOS    


def test_basic_identifiers():
    in_stream = FileWrapper(io.StringIO('x xs f0_0 foo_bar foo_bar_baz quix__'))
    l = Lexer(in_stream)
    t = l.next_token()
    assert t.token_type == TokenType.ID
    assert t.lexeme == 'x'
    assert t.line == 1
    assert t.column == 1
    t = l.next_token()
    assert t.token_type == TokenType.ID
    assert t.lexeme == 'xs'
    assert t.line == 1
    assert t.column == 3
    t = l.next_token()
    assert t.token_type == TokenType.ID
    assert t.lexeme == 'f0_0'
    assert t.line == 1
    assert t.column == 6
    t = l.next_token()
    assert t.token_type == TokenType.ID
    assert t.lexeme == 'foo_bar'
    assert t.line == 1
    assert t.column == 11
    t = l.next_token()
    assert t.token_type == TokenType.ID
    assert t.lexeme == 'foo_bar_baz'
    assert t.line == 1
    assert t.column == 19
    t = l.next_token()
    assert t.token_type == TokenType.ID
    assert t.lexeme == 'quix__'
    assert t.line == 1
    assert t.column == 31
    assert l.next_token().token_type == TokenType.EOS    
    

def test_with_comments():
    in_stream = FileWrapper(io.StringIO('x < 1 // test 1\nif 3.14'))
    l = Lexer(in_stream)
    t = l.next_token()
    assert t.token_type == TokenType.ID
    assert t.lexeme == 'x'
    assert t.line == 1
    assert t.column == 1
    t = l.next_token()
    assert t.token_type == TokenType.LESS
    assert t.lexeme == '<'
    assert t.line == 1
    assert t.column == 3
    t = l.next_token()
    assert t.token_type == TokenType.INT_VAL
    assert t.lexeme == '1'
    assert t.line == 1
    assert t.column == 5
    t = l.next_token()
    assert t.token_type == TokenType.COMMENT
    assert t.lexeme == ' test 1'
    assert t.line == 1
    assert t.column == 7
    t = l.next_token()
    assert t.token_type == TokenType.IF
    assert t.lexeme == 'if'
    assert t.line == 2
    assert t.column == 1
    t = l.next_token()
    assert t.token_type == TokenType.DOUBLE_VAL
    assert t.lexeme == '3.14'
    assert t.line == 2
    assert t.column == 4
    assert l.next_token().token_type == TokenType.EOS    

    
def test_no_spaces_tokens():
    in_stream = FileWrapper(io.StringIO('for(int x)ify=4;'))
    l = Lexer(in_stream)
    t = l.next_token()
    assert t.token_type == TokenType.FOR
    assert t.lexeme == 'for'
    assert t.line == 1
    assert t.column == 1
    t = l.next_token()
    assert t.token_type == TokenType.LPAREN
    assert t.lexeme == '('
    assert t.line == 1
    assert t.column == 4
    t = l.next_token()
    assert t.token_type == TokenType.INT_TYPE
    assert t.lexeme == 'int'
    assert t.line == 1
    assert t.column == 5
    t = l.next_token()
    assert t.token_type == TokenType.ID
    assert t.lexeme == 'x'
    assert t.line == 1
    assert t.column == 9
    t = l.next_token()
    assert t.token_type == TokenType.RPAREN
    assert t.lexeme == ')'
    assert t.line == 1
    assert t.column == 10
    t = l.next_token()
    assert t.token_type == TokenType.ID
    assert t.lexeme == 'ify'
    assert t.line == 1
    assert t.column == 11
    t = l.next_token()
    assert t.token_type == TokenType.ASSIGN
    assert t.lexeme == '='
    assert t.line == 1
    assert t.column == 14
    t = l.next_token()
    assert t.token_type == TokenType.INT_VAL
    assert t.lexeme == '4'
    assert t.line == 1
    assert t.column == 15
    t = l.next_token()
    assert t.token_type == TokenType.SEMICOLON
    assert t.lexeme == ';'
    assert t.line == 1
    assert t.column == 16
    assert l.next_token().token_type == TokenType.EOS        

    
def test_no_spaces_numbers():
    in_stream = FileWrapper(io.StringIO('32.1.42 .0.0'))
    l = Lexer(in_stream)
    t = l.next_token()
    assert t.token_type == TokenType.DOUBLE_VAL
    assert t.lexeme == '32.1'
    assert t.line == 1
    assert t.column == 1
    t = l.next_token()
    assert t.token_type == TokenType.DOT
    assert t.lexeme == '.'
    assert t.line == 1
    assert t.column == 5
    t = l.next_token()
    assert t.token_type == TokenType.INT_VAL
    assert t.lexeme == '42'
    assert t.line == 1
    assert t.column == 6
    t = l.next_token()
    assert t.token_type == TokenType.DOT
    assert t.lexeme == '.'
    assert t.line == 1
    assert t.column == 9
    t = l.next_token()
    assert t.token_type == TokenType.DOUBLE_VAL
    assert t.lexeme == '0.0'
    assert t.line == 1
    assert t.column == 10
    assert l.next_token().token_type == TokenType.EOS        

    
def test_non_terminated_string():
    in_stream = FileWrapper(io.StringIO('"hello \nworld"'))
    l = Lexer(in_stream)
    with pytest.raises(MyPLError) as e:
        l.next_token()
    assert str(e.value).startswith('Lexer Error')

    
def test_invalid_not():
    in_stream = FileWrapper(io.StringIO('!>'))
    l = Lexer(in_stream)
    with pytest.raises(MyPLError) as e:
        l.next_token()
    assert str(e.value).startswith('Lexer Error')
    in_stream = FileWrapper(io.StringIO('!'))
    l = Lexer(in_stream)
    with pytest.raises(MyPLError) as e:
        l.next_token()
    assert str(e.value).startswith('Lexer Error')

    
def test_missing_double_digit():
    in_stream = FileWrapper(io.StringIO('32.a'))
    l = Lexer(in_stream)
    with pytest.raises(MyPLError) as e:
        l.next_token()
    assert str(e.value).startswith('Lexer Error')

    
def test_leading_zero():
    in_stream = FileWrapper(io.StringIO('02'))
    l = Lexer(in_stream)
    with pytest.raises(MyPLError) as e:
        l.next_token()
    assert str(e.value).startswith('Lexer Error')
    in_stream = FileWrapper(io.StringIO('02.1'))
    l = Lexer(in_stream)
    with pytest.raises(MyPLError) as e:
        l.next_token()
    assert str(e.value).startswith('Lexer Error')


def test_invalid_symbol():
    # note: there are more illegal symbols than these two
    in_stream = FileWrapper(io.StringIO('#'))
    l = Lexer(in_stream)
    with pytest.raises(MyPLError) as e:
        l.next_token()
    assert str(e.value).startswith('Lexer Error')
    in_stream = FileWrapper(io.StringIO('?'))
    l = Lexer(in_stream)
    with pytest.raises(MyPLError) as e:
        l.next_token()
    assert str(e.value).startswith('Lexer Error')

    
def test_invalid_id():
    # note: there are more illegal symbols than these two
    in_stream = FileWrapper(io.StringIO('_xs'))
    l = Lexer(in_stream)
    with pytest.raises(MyPLError) as e:
        l.next_token()
    assert str(e.value).startswith('Lexer Error')


#----------------------------------------------------------------------
# AST PARSER TESTING
#----------------------------------------------------------------------

def test_empty_input():
    in_stream = FileWrapper(io.StringIO(''))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs) == 0
    assert len(p.struct_defs) == 0

def test_empty_fun():
    in_stream = FileWrapper(io.StringIO('int f() {}'))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs) == 1
    assert len(p.struct_defs) == 0
    assert p.fun_defs[0].return_type.type_name.lexeme == 'int'
    assert p.fun_defs[0].return_type.is_array == False
    assert p.fun_defs[0].fun_name.lexeme == 'f'
    assert len(p.fun_defs[0].params) == 0
    assert len(p.fun_defs[0].stmts) == 0

def test_empty_fun_array_return():
    in_stream = FileWrapper(io.StringIO('array int f() {}'))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs) == 1
    assert p.fun_defs[0].return_type.type_name.lexeme == 'int'
    assert p.fun_defs[0].return_type.is_array == True
    assert p.fun_defs[0].fun_name.lexeme == 'f'
    assert len(p.fun_defs[0].params) == 0
    assert len(p.fun_defs[0].stmts) == 0

def test_empty_fun_one_param():
    in_stream = FileWrapper(io.StringIO('int f(string x) {}'))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs) == 1
    assert len(p.fun_defs[0].params) == 1
    assert p.fun_defs[0].params[0].data_type.is_array == False
    assert p.fun_defs[0].params[0].data_type.type_name.lexeme == 'string'
    assert p.fun_defs[0].params[0].var_name.lexeme == 'x'    

def test_empty_fun_one_id_param():
    in_stream = FileWrapper(io.StringIO('int f(S s1) {}'))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs) == 1
    assert len(p.fun_defs[0].params) == 1
    assert p.fun_defs[0].params[0].data_type.is_array == False
    assert p.fun_defs[0].params[0].data_type.type_name.lexeme == 'S'
    assert p.fun_defs[0].params[0].var_name.lexeme == 's1'    

def test_empty_fun_one_array_param():
    in_stream = FileWrapper(io.StringIO('int f(array int ys) {}'))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs) == 1
    assert len(p.fun_defs[0].params) == 1
    assert p.fun_defs[0].params[0].data_type.is_array == True
    assert p.fun_defs[0].params[0].data_type.type_name.lexeme == 'int'
    assert p.fun_defs[0].params[0].var_name.lexeme == 'ys'    

def test_empty_fun_two_params():
    in_stream = FileWrapper(io.StringIO('int f(bool x, int y) {}'))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs) == 1
    assert len(p.fun_defs[0].params) == 2
    assert p.fun_defs[0].params[0].data_type.is_array == False
    assert p.fun_defs[0].params[0].data_type.type_name.lexeme == 'bool'
    assert p.fun_defs[0].params[0].var_name.lexeme == 'x'    
    assert p.fun_defs[0].params[1].data_type.is_array == False
    assert p.fun_defs[0].params[1].data_type.type_name.lexeme == 'int'
    assert p.fun_defs[0].params[1].var_name.lexeme == 'y'    

def test_empty_fun_three_params():
    in_stream = FileWrapper(io.StringIO('int f(bool x, int y, array string z) {}'))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs) == 1
    assert len(p.fun_defs[0].params) == 3
    assert p.fun_defs[0].params[0].data_type.is_array == False
    assert p.fun_defs[0].params[0].data_type.type_name.lexeme == 'bool'
    assert p.fun_defs[0].params[0].var_name.lexeme == 'x'    
    assert p.fun_defs[0].params[1].data_type.is_array == False
    assert p.fun_defs[0].params[1].data_type.type_name.lexeme == 'int'
    assert p.fun_defs[0].params[1].var_name.lexeme == 'y'    
    assert p.fun_defs[0].params[2].data_type.is_array == True
    assert p.fun_defs[0].params[2].data_type.type_name.lexeme == 'string'
    assert p.fun_defs[0].params[2].var_name.lexeme == 'z'    

def test_multiple_empty_funs():
    in_stream = FileWrapper(io.StringIO(
        'void f() {}\n'
        'int g() {}\n'
        ''
    ))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs) == 2
    assert len(p.struct_defs) == 0
    
    
#----------------------------------------------------------------------
# Basic Struct Definitions
#----------------------------------------------------------------------

def test_empty_struct():
    in_stream = FileWrapper(io.StringIO('struct S {}'))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs) == 0
    assert len(p.struct_defs) == 1
    assert p.struct_defs[0].struct_name.lexeme == 'S'
    assert len(p.struct_defs[0].fields) == 0

def test_one_base_type_field_struct():
    in_stream = FileWrapper(io.StringIO('struct S {int x;}'))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs) == 0
    assert len(p.struct_defs) == 1
    assert p.struct_defs[0].struct_name.lexeme == 'S'
    assert len(p.struct_defs[0].fields) == 1
    assert p.struct_defs[0].fields[0].data_type.is_array == False
    assert p.struct_defs[0].fields[0].data_type.type_name.lexeme == 'int'
    assert p.struct_defs[0].fields[0].var_name.lexeme == 'x'

def test_one_id_field_struct():
    in_stream = FileWrapper(io.StringIO('struct S {S s1;}'))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs) == 0
    assert len(p.struct_defs) == 1
    assert p.struct_defs[0].struct_name.lexeme == 'S'
    assert len(p.struct_defs[0].fields) == 1
    assert p.struct_defs[0].fields[0].data_type.is_array == False
    assert p.struct_defs[0].fields[0].data_type.type_name.lexeme == 'S'
    assert p.struct_defs[0].fields[0].var_name.lexeme == 's1'

def test_one_array_field_struct():
    in_stream = FileWrapper(io.StringIO('struct S {array int x1;}'))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs) == 0
    assert len(p.struct_defs) == 1
    assert p.struct_defs[0].struct_name.lexeme == 'S'
    assert len(p.struct_defs[0].fields) == 1
    assert p.struct_defs[0].fields[0].data_type.is_array == True
    assert p.struct_defs[0].fields[0].data_type.type_name.lexeme == 'int'
    assert p.struct_defs[0].fields[0].var_name.lexeme == 'x1'

def test_two_field_struct():
    in_stream = FileWrapper(io.StringIO('struct S {int x1; bool x2;}'))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs) == 0
    assert len(p.struct_defs) == 1
    assert p.struct_defs[0].struct_name.lexeme == 'S'
    assert len(p.struct_defs[0].fields) == 2
    assert p.struct_defs[0].fields[0].data_type.is_array == False
    assert p.struct_defs[0].fields[0].data_type.type_name.lexeme == 'int'
    assert p.struct_defs[0].fields[0].var_name.lexeme == 'x1'
    assert p.struct_defs[0].fields[1].data_type.is_array == False
    assert p.struct_defs[0].fields[1].data_type.type_name.lexeme == 'bool'
    assert p.struct_defs[0].fields[1].var_name.lexeme == 'x2'

def test_three_field_struct():
    in_stream = FileWrapper(io.StringIO(
        'struct S {int x1; bool x2; array S x3;}'
    ))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs) == 0
    assert len(p.struct_defs) == 1
    assert p.struct_defs[0].struct_name.lexeme == 'S'
    assert len(p.struct_defs[0].fields) == 3
    assert p.struct_defs[0].fields[0].data_type.is_array == False
    assert p.struct_defs[0].fields[0].data_type.type_name.lexeme == 'int'
    assert p.struct_defs[0].fields[0].var_name.lexeme == 'x1'
    assert p.struct_defs[0].fields[1].data_type.is_array == False
    assert p.struct_defs[0].fields[1].data_type.type_name.lexeme == 'bool'
    assert p.struct_defs[0].fields[1].var_name.lexeme == 'x2'
    assert p.struct_defs[0].fields[2].data_type.is_array == True
    assert p.struct_defs[0].fields[2].data_type.type_name.lexeme == 'S'
    assert p.struct_defs[0].fields[2].var_name.lexeme == 'x3'

def test_empty_struct_and_fun():
    in_stream = FileWrapper(io.StringIO(
        'struct S1 {} \n'
        'int f() {} \n'
        'struct S2 {} \n'
        'int g() {} \n'
        'struct S3 {} \n'
    ))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs) == 2
    assert len(p.struct_defs) == 3
    assert p.fun_defs[0].fun_name.lexeme == 'f'
    assert p.fun_defs[1].fun_name.lexeme == 'g'
    assert p.struct_defs[0].struct_name.lexeme == 'S1'
    assert p.struct_defs[1].struct_name.lexeme == 'S2'    
    assert p.struct_defs[2].struct_name.lexeme == 'S3'    

    
#----------------------------------------------------------------------
# Variable Declaration Statements
#----------------------------------------------------------------------

def test_var_base_type_var_decls():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  int x1; \n'
        '  double x2; \n'
        '  bool x3; \n'
        '  string x4; \n'
        '} \n'
    ))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs[0].stmts) == 4
    assert p.fun_defs[0].stmts[0].var_def.data_type.is_array == False
    assert p.fun_defs[0].stmts[1].var_def.data_type.is_array == False
    assert p.fun_defs[0].stmts[2].var_def.data_type.is_array == False
    assert p.fun_defs[0].stmts[3].var_def.data_type.is_array == False    
    assert p.fun_defs[0].stmts[0].var_def.data_type.type_name.lexeme == 'int'
    assert p.fun_defs[0].stmts[1].var_def.data_type.type_name.lexeme == 'double'
    assert p.fun_defs[0].stmts[2].var_def.data_type.type_name.lexeme == 'bool'
    assert p.fun_defs[0].stmts[3].var_def.data_type.type_name.lexeme == 'string'
    assert p.fun_defs[0].stmts[0].var_def.var_name.lexeme == 'x1'
    assert p.fun_defs[0].stmts[1].var_def.var_name.lexeme == 'x2'
    assert p.fun_defs[0].stmts[2].var_def.var_name.lexeme == 'x3'
    assert p.fun_defs[0].stmts[3].var_def.var_name.lexeme == 'x4'

def test_array_var_decl():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  array int x1; \n'
        '} \n'
    ))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs[0].stmts) == 1
    assert p.fun_defs[0].stmts[0].var_def.data_type.is_array == True
    assert p.fun_defs[0].stmts[0].var_def.data_type.type_name.lexeme == 'int'
    assert p.fun_defs[0].stmts[0].var_def.var_name.lexeme == 'x1'    

def test_id_var_decl():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  S s1; \n'
        '} \n'
    ))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs[0].stmts) == 1
    assert p.fun_defs[0].stmts[0].var_def.data_type.is_array == False
    assert p.fun_defs[0].stmts[0].var_def.data_type.type_name.lexeme == 'S'
    assert p.fun_defs[0].stmts[0].var_def.var_name.lexeme == 's1'    
    

def test_base_type_var_def():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  int x1 = 0; \n'
        '} \n'
    ))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs[0].stmts) == 1
    assert p.fun_defs[0].stmts[0].var_def.data_type.is_array == False
    assert p.fun_defs[0].stmts[0].var_def.data_type.type_name.lexeme == 'int'
    assert p.fun_defs[0].stmts[0].var_def.var_name.lexeme == 'x1'
    print(p.fun_defs[0].stmts[0].expr)
    assert p.fun_defs[0].stmts[0].expr.not_op == False
    assert p.fun_defs[0].stmts[0].expr.first.rvalue.value.lexeme == '0'

def test_id_var_def():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  Node my_node = null; \n'
        '} \n'
    ))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs[0].stmts) == 1
    assert p.fun_defs[0].stmts[0].var_def.data_type.is_array == False
    assert p.fun_defs[0].stmts[0].var_def.data_type.type_name.lexeme == 'Node'
    assert p.fun_defs[0].stmts[0].var_def.var_name.lexeme == 'my_node'
    assert p.fun_defs[0].stmts[0].expr.not_op == False
    assert p.fun_defs[0].stmts[0].expr.first.rvalue.value.lexeme == 'null'
    
def test_array_var_def():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  array bool my_bools = null; \n'
        '  array Node my_nodes = null; \n'
        '} \n'
    ))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs[0].stmts) == 2
    assert p.fun_defs[0].stmts[0].var_def.data_type.is_array == True
    assert p.fun_defs[0].stmts[0].var_def.data_type.type_name.lexeme == 'bool'
    assert p.fun_defs[0].stmts[0].var_def.var_name.lexeme == 'my_bools'
    assert p.fun_defs[0].stmts[0].expr.not_op == False
    assert p.fun_defs[0].stmts[0].expr.first.rvalue.value.lexeme == 'null'
    assert p.fun_defs[0].stmts[1].var_def.data_type.is_array == True
    assert p.fun_defs[0].stmts[1].var_def.data_type.type_name.lexeme == 'Node'
    assert p.fun_defs[0].stmts[1].var_def.var_name.lexeme == 'my_nodes'
    assert p.fun_defs[0].stmts[1].expr.not_op == False
    assert p.fun_defs[0].stmts[1].expr.first.rvalue.value.lexeme == 'null'

    
#----------------------------------------------------------------------
# Assignment Statements
#----------------------------------------------------------------------

def test_simple_assignment():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  x = null; \n'
        '} \n'
    ))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs[0].stmts) == 1
    assert p.fun_defs[0].stmts[0].lvalue[0].var_name.lexeme == 'x'
    assert p.fun_defs[0].stmts[0].lvalue[0].array_expr == None
    assert p.fun_defs[0].stmts[0].expr.not_op == False
    assert p.fun_defs[0].stmts[0].expr.first.rvalue.value.lexeme == 'null'
    assert p.fun_defs[0].stmts[0].expr.rest == None

def test_simple_path_assignment():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  x.y = null; \n'
        '} \n'
    ))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs[0].stmts) == 1
    assert p.fun_defs[0].stmts[0].lvalue[0].var_name.lexeme == 'x'
    assert p.fun_defs[0].stmts[0].lvalue[0].array_expr == None
    assert p.fun_defs[0].stmts[0].lvalue[1].var_name.lexeme == 'y'
    assert p.fun_defs[0].stmts[0].lvalue[1].array_expr == None
    assert p.fun_defs[0].stmts[0].expr.not_op == False
    assert p.fun_defs[0].stmts[0].expr.first.rvalue.value.lexeme == 'null'
    assert p.fun_defs[0].stmts[0].expr.rest == None

def test_simple_array_assignment():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  x[0] = null; \n'
        '} \n'
    ))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs[0].stmts) == 1
    stmt = p.fun_defs[0].stmts[0]
    assert stmt.lvalue[0].var_name.lexeme == 'x'
    assert stmt.lvalue[0].array_expr.not_op == False
    assert stmt.lvalue[0].array_expr.first.rvalue.value.lexeme == '0'
    assert stmt.lvalue[0].array_expr.rest == None
    assert stmt.expr.not_op == False
    assert stmt.expr.first.rvalue.value.lexeme == 'null'
    assert stmt.expr.rest == None

def test_multiple_path_assignment():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  x1.x2[0].x3.x4[1] = null; \n'
        '} \n'
    ))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs[0].stmts) == 1
    stmt = p.fun_defs[0].stmts[0]
    assert len(stmt.lvalue) == 4
    assert stmt.lvalue[0].var_name.lexeme == 'x1'
    assert stmt.lvalue[0].array_expr == None
    assert stmt.lvalue[1].var_name.lexeme == 'x2'    
    assert stmt.lvalue[1].array_expr.not_op == False
    assert stmt.lvalue[1].array_expr.first.rvalue.value.lexeme == '0'
    assert stmt.lvalue[2].var_name.lexeme == 'x3'
    assert stmt.lvalue[2].array_expr == None
    assert stmt.lvalue[3].var_name.lexeme == 'x4'
    assert stmt.lvalue[3].array_expr.not_op == False
    assert stmt.lvalue[3].array_expr.first.rvalue.value.lexeme == '1'

    
#----------------------------------------------------------------------
# If Statements
#----------------------------------------------------------------------

def test_single_if_statement():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  if (true) {} \n'
        '} \n'
    ))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs[0].stmts) == 1
    stmt = p.fun_defs[0].stmts[0]
    assert stmt.if_part.condition.first.rvalue.value.lexeme == 'true'
    assert len(stmt.if_part.stmts) == 0
    assert len(stmt.else_ifs) == 0
    assert len(stmt.else_stmts) == 0
    
def test_if_statement_with_body():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  if (true) {int x = 0;} \n'
        '} \n'
    ))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs[0].stmts) == 1
    stmt = p.fun_defs[0].stmts[0]
    assert stmt.if_part.condition.first.rvalue.value.lexeme == 'true'
    assert len(stmt.if_part.stmts) == 1
    assert len(stmt.else_ifs) == 0
    assert len(stmt.else_stmts) == 0

def test_if_statement_with_one_else_if():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  if (true) {} \n'
        '  elseif (false) {} \n'
        '} \n'
    ))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs[0].stmts) == 1
    stmt = p.fun_defs[0].stmts[0]
    assert stmt.if_part.condition.first.rvalue.value.lexeme == 'true'
    assert len(stmt.if_part.stmts) == 0
    assert len(stmt.else_ifs) == 1
    assert stmt.else_ifs[0].condition.first.rvalue.value.lexeme == 'false'
    assert len(stmt.else_ifs[0].stmts) == 0

    
def test_if_statement_with_two_else_ifs():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  if (true) {} \n'
        '  elseif (false) {} \n'
        '  elseif (true) {} \n'
        '} \n'
    ))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs[0].stmts) == 1
    stmt = p.fun_defs[0].stmts[0]
    assert stmt.if_part.condition.first.rvalue.value.lexeme == 'true'
    assert len(stmt.if_part.stmts) == 0
    assert len(stmt.else_ifs) == 2
    assert stmt.else_ifs[0].condition.first.rvalue.value.lexeme == 'false'
    assert len(stmt.else_ifs[0].stmts) == 0
    assert stmt.else_ifs[1].condition.first.rvalue.value.lexeme == 'true'
    assert len(stmt.else_ifs[1].stmts) == 0
    assert len(stmt.else_stmts) == 0

def test_if_statement_with_empty_else():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  if (true) {} \n'
        '  else {} \n'
        '} \n'
    ))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs[0].stmts) == 1
    stmt = p.fun_defs[0].stmts[0]
    assert stmt.if_part.condition.first.rvalue.value.lexeme == 'true'
    assert len(stmt.if_part.stmts) == 0
    assert len(stmt.else_ifs) == 0
    assert len(stmt.else_stmts) == 0

def test_if_statement_with_non_empty_else():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  if (true) {} \n'
        '  else {x = 5;} \n'
        '} \n'
    ))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs[0].stmts) == 1
    stmt = p.fun_defs[0].stmts[0]
    assert stmt.if_part.condition.first.rvalue.value.lexeme == 'true'
    assert len(stmt.if_part.stmts) == 0
    assert len(stmt.else_ifs) == 0
    assert len(stmt.else_stmts) == 1

def test_full_if_statement():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  if (true) {x = 5;} \n'
        '  elseif (false) {x = 6;} \n'
        '  else {x = 7;} \n'
        '} \n'
    ))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs[0].stmts) == 1
    stmt = p.fun_defs[0].stmts[0]
    assert stmt.if_part.condition.first.rvalue.value.lexeme == 'true'
    assert len(stmt.if_part.stmts) == 1
    assert len(stmt.else_ifs) == 1
    assert stmt.else_ifs[0].condition.first.rvalue.value.lexeme == 'false'
    assert len(stmt.else_ifs[0].stmts) == 1
    assert len(stmt.else_stmts) == 1

    
#----------------------------------------------------------------------
# While Statements
#----------------------------------------------------------------------

def test_empty_while_statement():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  while (true) {} \n'
        '} \n'
    ))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs[0].stmts) == 1
    stmt = p.fun_defs[0].stmts[0]
    assert stmt.condition.first.rvalue.value.lexeme == 'true'
    assert len(stmt.stmts) == 0

def test_while_statement_with_body():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  while (true) {x = 5;} \n'
        '} \n'
    ))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs[0].stmts) == 1
    stmt = p.fun_defs[0].stmts[0]
    assert stmt.condition.first.rvalue.value.lexeme == 'true'
    assert len(stmt.stmts) == 1

    
#----------------------------------------------------------------------
# Expressions
#----------------------------------------------------------------------

def test_literals():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  x = true; \n'
        '  x = false; \n'        
        '  x = 0; \n'
        '  x = 0.0; \n'
        '  x = "a"; \n'
        '} \n'
    ))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs[0].stmts) == 5
    assert p.fun_defs[0].stmts[0].expr.first.rvalue.value.lexeme == 'true'
    assert p.fun_defs[0].stmts[1].expr.first.rvalue.value.lexeme == 'false'
    assert p.fun_defs[0].stmts[2].expr.first.rvalue.value.lexeme == '0'    
    assert p.fun_defs[0].stmts[3].expr.first.rvalue.value.lexeme == '0.0'    
    assert p.fun_defs[0].stmts[4].expr.first.rvalue.value.lexeme == 'a'        
    assert p.fun_defs[0].stmts[0].expr.not_op == False
    assert p.fun_defs[0].stmts[1].expr.not_op == False
    assert p.fun_defs[0].stmts[2].expr.not_op == False
    assert p.fun_defs[0].stmts[3].expr.not_op == False
    assert p.fun_defs[0].stmts[4].expr.not_op == False

def test_simple_bool_expr():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  x = true and false; \n'
        '} \n'
    ))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs[0].stmts) == 1
    stmt = p.fun_defs[0].stmts[0]
    assert stmt.expr.not_op == False
    assert stmt.expr.first.rvalue.value.lexeme == 'true'
    assert stmt.expr.op.lexeme == 'and'
    assert stmt.expr.rest.not_op == False
    assert stmt.expr.rest.first.rvalue.value.lexeme == 'false'
    assert stmt.expr.rest.op == None
    assert stmt.expr.rest.rest == None    

def test_simple_not_bool_expr():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  x = not true and false; \n'
        '} \n'
    ))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs[0].stmts) == 1
    stmt = p.fun_defs[0].stmts[0]
    assert stmt.expr.not_op == True
    assert stmt.expr.first.rvalue.value.lexeme == 'true'
    assert stmt.expr.op.lexeme == 'and'
    assert stmt.expr.rest.not_op == False
    assert stmt.expr.rest.first.rvalue.value.lexeme == 'false'
    assert stmt.expr.rest.op == None
    assert stmt.expr.rest.rest == None    

def test_simple_paren_expr():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  x = (1 + 2); \n'
        '} \n'
    ))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs[0].stmts) == 1
    stmt = p.fun_defs[0].stmts[0]
    assert stmt.expr.not_op == False
    assert stmt.expr.first.expr.first.rvalue.value.lexeme == '1'
    assert stmt.expr.first.expr.op.lexeme == '+'
    assert stmt.expr.first.expr.rest.not_op == False
    assert stmt.expr.first.expr.rest.first.rvalue.value.lexeme == '2'
    assert stmt.expr.first.expr.rest.op == None
    assert stmt.expr.first.expr.rest.rest == None    

def test_expr_after_paren_expr():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  x = (1 + 2) - 3; \n'
        '} \n'
    ))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs[0].stmts) == 1
    stmt = p.fun_defs[0].stmts[0]
    assert stmt.expr.not_op == False
    assert stmt.expr.first.expr.first.rvalue.value.lexeme == '1'
    assert stmt.expr.first.expr.op.lexeme == '+'
    assert stmt.expr.first.expr.rest.not_op == False
    assert stmt.expr.first.expr.rest.first.rvalue.value.lexeme == '2'
    assert stmt.expr.first.expr.rest.op == None
    assert stmt.expr.first.expr.rest.rest == None    
    assert stmt.expr.op.lexeme == '-'
    assert stmt.expr.rest.not_op == False
    assert stmt.expr.rest.first.rvalue.value.lexeme == '3'
    assert stmt.expr.rest.op == None
    assert stmt.expr.rest.rest == None

def test_expr_before_paren_expr():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  x = 3 * (1 + 2); \n'
        '} \n'
    ))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs[0].stmts) == 1
    stmt = p.fun_defs[0].stmts[0]
    assert stmt.expr.not_op == False
    assert stmt.expr.first.rvalue.value.lexeme == '3'
    assert stmt.expr.op.lexeme == '*'
    assert stmt.expr.rest.not_op == False
    assert stmt.expr.rest.first.expr.first.rvalue.value.lexeme == '1'
    assert stmt.expr.rest.first.expr.op.lexeme == '+'
    assert stmt.expr.rest.first.expr.rest.not_op == False
    assert stmt.expr.rest.first.expr.rest.first.rvalue.value.lexeme == '2'
    assert stmt.expr.rest.first.expr.rest.op == None
    assert stmt.expr.rest.first.expr.rest.rest == None
    assert stmt.expr.rest.op == None
    assert stmt.expr.rest.rest == None

def test_expr_with_two_ops():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  x = 1 / 2 * 3; \n'
        '} \n'
    ))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs[0].stmts) == 1
    stmt = p.fun_defs[0].stmts[0]
    assert stmt.expr.not_op == False
    assert stmt.expr.first.rvalue.value.lexeme == '1'
    assert stmt.expr.op.lexeme == '/'
    assert stmt.expr.rest.not_op == False
    assert stmt.expr.rest.first.rvalue.value.lexeme == '2'
    assert stmt.expr.rest.op.lexeme == '*'
    assert stmt.expr.rest.rest.not_op == False
    assert stmt.expr.rest.rest.first.rvalue.value.lexeme == '3'
    assert stmt.expr.rest.rest.op == None
    assert stmt.expr.rest.rest.rest == None    

def test_empty_call_expr():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  f(); \n'
        '} \n'
    ))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs[0].stmts) == 1
    stmt = p.fun_defs[0].stmts[0]
    assert stmt.fun_name.lexeme == 'f'
    assert len(stmt.args) == 0

def test_one_arg_call_expr():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  f(3); \n'
        '} \n'
    ))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs[0].stmts) == 1
    stmt = p.fun_defs[0].stmts[0]
    assert stmt.fun_name.lexeme == 'f'
    assert len(stmt.args) == 1
    assert stmt.args[0].not_op == False
    assert stmt.args[0].first.rvalue.value.lexeme == '3'
    assert stmt.args[0].op == None
    assert stmt.args[0].rest == None    

def test_two_arg_call_expr():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  f(3, 4); \n'
        '} \n'
    ))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs[0].stmts) == 1
    stmt = p.fun_defs[0].stmts[0]
    assert stmt.fun_name.lexeme == 'f'
    assert len(stmt.args) == 2
    assert stmt.args[0].not_op == False
    assert stmt.args[0].first.rvalue.value.lexeme == '3'
    assert stmt.args[0].op == None
    assert stmt.args[0].rest == None    
    assert stmt.args[1].not_op == False
    assert stmt.args[1].first.rvalue.value.lexeme == '4'
    assert stmt.args[1].op == None
    assert stmt.args[1].rest == None    
    
def test_simple_struct_new_expr():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  x = new S(); \n'
        '} \n'
    ))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs[0].stmts) == 1
    stmt = p.fun_defs[0].stmts[0]
    assert stmt.expr.not_op == False
    assert stmt.expr.first.rvalue.type_name.lexeme == 'S'
    assert stmt.expr.first.rvalue.array_expr == None
    assert len(stmt.expr.first.rvalue.struct_params) == 0

def test_two_arg_struct_new_expr():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  x = new S(3, 4); \n'
        '} \n'
    ))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs[0].stmts) == 1
    stmt = p.fun_defs[0].stmts[0]
    assert stmt.expr.not_op == False
    assert stmt.expr.first.rvalue.type_name.lexeme == 'S'
    assert stmt.expr.first.rvalue.array_expr == None
    assert len(stmt.expr.first.rvalue.struct_params) == 2
    assert stmt.expr.first.rvalue.struct_params[0].first.rvalue.value.lexeme == '3'
    assert stmt.expr.first.rvalue.struct_params[1].first.rvalue.value.lexeme == '4'

def test_base_type_array_new_expr():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  x = new int[10]; \n'
        '} \n'
    ))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs[0].stmts) == 1
    stmt = p.fun_defs[0].stmts[0]
    assert stmt.expr.not_op == False
    assert stmt.expr.first.rvalue.type_name.lexeme == 'int'
    assert stmt.expr.first.rvalue.array_expr.first.rvalue.value.lexeme == '10'
    assert stmt.expr.first.rvalue.struct_params == None

def test_simple_var_rvalue():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  x = y; \n'
        '} \n'
    ))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs[0].stmts) == 1
    stmt = p.fun_defs[0].stmts[0]
    assert stmt.expr.not_op == False
    assert len(stmt.expr.first.rvalue.path) == 1
    assert stmt.expr.first.rvalue.path[0].var_name.lexeme == 'y'
    assert stmt.expr.first.rvalue.path[0].array_expr == None

def test_simple_array_var_rvalue():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  x = y[0]; \n'
        '} \n'
    ))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs[0].stmts) == 1
    stmt = p.fun_defs[0].stmts[0]
    assert len(stmt.expr.first.rvalue.path) == 1
    assert stmt.expr.first.rvalue.path[0].var_name.lexeme == 'y'
    assert stmt.expr.first.rvalue.path[0].array_expr.not_op == False
    assert stmt.expr.first.rvalue.path[0].array_expr.first.rvalue.value.lexeme == '0'
    assert stmt.expr.first.rvalue.path[0].array_expr.op == None
    assert stmt.expr.first.rvalue.path[0].array_expr.rest == None

def test_two_path_var_rvalue():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  x = y.z; \n'
        '} \n'
    ))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs[0].stmts) == 1
    stmt = p.fun_defs[0].stmts[0]
    assert len(stmt.expr.first.rvalue.path) == 2
    assert stmt.expr.first.rvalue.path[0].var_name.lexeme == 'y'
    assert stmt.expr.first.rvalue.path[0].array_expr == None
    assert stmt.expr.first.rvalue.path[1].var_name.lexeme == 'z'
    assert stmt.expr.first.rvalue.path[1].array_expr == None


def test_mixed_path_var_rvalue():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  x = u[2].v.w[1].y; \n'
        '} \n'
    ))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs[0].stmts) == 1
    stmt = p.fun_defs[0].stmts[0]
    assert len(stmt.expr.first.rvalue.path) == 4
    assert stmt.expr.not_op == False
    assert stmt.expr.op == None
    assert stmt.expr.rest == None
    path = stmt.expr.first.rvalue.path
    assert path[0].var_name.lexeme == 'u'
    assert path[0].array_expr.not_op == False
    assert path[0].array_expr.first.rvalue.value.lexeme == '2'
    assert path[0].array_expr.op == None
    assert path[0].array_expr.rest == None
    assert path[1].var_name.lexeme == 'v'
    assert path[1].array_expr == None
    assert path[2].var_name.lexeme == 'w'
    assert path[2].array_expr.not_op == False
    assert path[2].array_expr.first.rvalue.value.lexeme == '1'
    assert path[2].array_expr.op == None
    assert path[2].array_expr.rest == None
    assert path[3].var_name.lexeme == 'y'
    assert path[3].array_expr == None


#----------------------------------------------------------------------
# TODO: Add at least 10 of your own tests below. Define at least two
# tests for statements, one test for return statements, five tests
# for expressions, and two tests that are more involved combining
# multiple constructs.
#----------------------------------------------------------------------

# Two for statement tests
def test_for_loop_condition():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  for (int i = 0; i < 10; i = i+1){} \n'
        '} \n'
    ))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs[0].stmts) == 1
    stmt = p.fun_defs[0].stmts[0]
    assert stmt.var_decl.var_def.var_name.lexeme == "i"
    assert stmt.condition.op.token_type == TokenType.LESS
    assert stmt.assign_stmt.lvalue[0].var_name.lexeme == "i"
    assert len(stmt.stmts) == 0

def test_for_loop_body():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  for (int i = 0; i < 10; i = i+1){\n'
        '       int x = i + 1; \n'
        '       x = 4 * x; \n}'
        '} \n'
    ))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs[0].stmts) == 1
    stmt = p.fun_defs[0].stmts[0]
    assert stmt.var_decl.var_def.var_name.lexeme == "i"
    assert stmt.condition.op.token_type == TokenType.LESS
    assert stmt.assign_stmt.lvalue[0].var_name.lexeme == "i"
    assert len(stmt.stmts) == 2

# One return statement test
def test_recursion_return_stmt():
    in_stream = FileWrapper(io.StringIO(
        'int recurse(int x) { \n'
        '   if(x == 18){return x;}\n'
        '   return recurse(x); \n'
        '} \n'
    ))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs[0].stmts) == 2
    ret_stmt1 = p.fun_defs[0].stmts[0]
    ret_stmt2 = p.fun_defs[0].stmts[1]
    assert ret_stmt1.if_part.stmts[0].expr.not_op == False
    assert ret_stmt1.if_part.stmts[0].expr.first.rvalue.path[0].var_name.lexeme == 'x'
    assert ret_stmt2.expr.not_op == False
    assert ret_stmt2.expr.first.rvalue.fun_name.lexeme == 'recurse'

# Five expression tests
def test_expr_node_with_empty_params():
    in_stream = FileWrapper(io.StringIO(
        'int main() { \n'
        '   if(not x){}\n'
        '} \n'
    ))
    p = ASTParser(Lexer(in_stream)).parse()
    stmt = p.fun_defs[0].stmts[0]
    assert stmt.if_part.condition.not_op == True
    assert stmt.if_part.condition.first.rvalue.path[0].var_name.lexeme == 'x'
    assert stmt.if_part.condition.op == None
    assert stmt.if_part.condition.rest == None

def test_array_expr_with_call_expr():
    in_stream = FileWrapper(io.StringIO(
        'int main() { \n'
        '   x[findIdx(z)] = 4;\n'
        '} \n'
    ))
    p = ASTParser(Lexer(in_stream)).parse()
    stmt = p.fun_defs[0].stmts[0]
    assert stmt.lvalue[0].var_name.lexeme == 'x'
    assert stmt.lvalue[0].array_expr.first.rvalue.fun_name.lexeme == 'findIdx'
    assert stmt.lvalue[0].array_expr.first.rvalue.args[0].first.rvalue.path[0].var_name.lexeme == 'z'

def test_expr_multiple_simple_var_rvalue():
    in_stream = FileWrapper(io.StringIO(
        'int main() { \n'
        '   x = 4 + 8 * 12 - 13 / 5;\n'
        '} \n'
    ))
    p = ASTParser(Lexer(in_stream)).parse()
    stmt = p.fun_defs[0].stmts[0]
    assert stmt.lvalue[0].var_name.lexeme == 'x'
    assert stmt.expr.op.lexeme == '+'
    assert stmt.expr.rest.op.lexeme == '*'
    assert stmt.expr.rest.rest.op.lexeme == '-'
    assert stmt.expr.rest.rest.rest.op.lexeme == '/'

def test_expr_multiple_path_and_call_expr():
    in_stream = FileWrapper(io.StringIO(
        'int main() { \n'
        '   x = addOne(y) - x[2].y.z.x[3] * triple(x);\n'
        '} \n'
    ))
    p = ASTParser(Lexer(in_stream)).parse()
    stmt = p.fun_defs[0].stmts[0]
    assert stmt.expr.first.rvalue.fun_name.lexeme == 'addOne'
    assert stmt.expr.op.lexeme == '-'
    assert stmt.expr.rest.first.rvalue.path[0].var_name.lexeme == 'x'
    assert stmt.expr.rest.first.rvalue.path[2].var_name.lexeme == 'z'
    assert stmt.expr.rest.op.lexeme == '*'
    assert stmt.expr.rest.rest.first.rvalue.fun_name.lexeme == 'triple'

def test_expr_new_rvalue_and_call_expr():
    in_stream = FileWrapper(io.StringIO(
        'int main() { \n'
        '   myStruct x1 = new myStruct(changeInt(z), build(r));\n'
        '} \n'
    ))
    p = ASTParser(Lexer(in_stream)).parse()
    stmt = p.fun_defs[0].stmts[0]
    assert stmt.var_def.data_type.type_name.token_type == TokenType.ID
    assert stmt.var_def.var_name.lexeme == 'x1'
    assert stmt.expr.first.rvalue.type_name.lexeme == 'myStruct'
    assert stmt.expr.first.rvalue.struct_params[0].first.rvalue.fun_name.lexeme == 'changeInt'
    assert stmt.expr.first.rvalue.struct_params[1].first.rvalue.fun_name.lexeme == 'build'

# Three more involved tests that involve multiple constructs
def test_nested_loops_and_conditionals():
    in_stream = FileWrapper(io.StringIO(
        'int main() { \n'
        '   if (y == true)\n'
        '   { while (x == 1){}}\n'
        '   else\n'
        '   { for (int i = 0; i < 10; i = i+1){}}\n'
        '} \n'
    ))
    p = ASTParser(Lexer(in_stream)).parse()
    stmt = p.fun_defs[0].stmts[0]
    assert stmt.if_part.stmts[0].condition.first.rvalue.path[0].var_name.lexeme == 'x'
    assert stmt.if_part.stmts[0].stmts == []
    assert stmt.else_stmts[0].var_decl.var_def.var_name.lexeme == 'i'
    assert stmt.else_stmts[0].condition.op.lexeme == '<'
    assert stmt.else_stmts[0].stmts == []

def test_while_stmt_with_call_expr():
    in_stream = FileWrapper(io.StringIO(
        'int main() { \n'
        '   while(getStatus(x.y[2])){}\n'
        '} \n'
    ))
    p = ASTParser(Lexer(in_stream)).parse()
    stmt = p.fun_defs[0].stmts[0]
    stmt.condition.first.rvalue.fun_name.lexeme == 'getStatus'
    stmt.condition.first.rvalue.args[0].first.rvalue.path[0].var_name.lexeme == 'x'
    stmt.condition.first.rvalue.args[0].first.rvalue.path[1].var_name.lexeme == 'y'
    stmt.condition.first.rvalue.args[0].first.rvalue.path[1].array_expr.first.rvalue.value.lexeme == 'y'

def test_var_decl_with_mixed_assignment():
    in_stream = FileWrapper(io.StringIO(
        'int main() { \n'
        '   int g = z.y[0].r + i[1].h.my_var[4] - h.e.m;'
        '} \n'
    ))
    p = ASTParser(Lexer(in_stream)).parse()
    stmt = p.fun_defs[0].stmts[0]
    assert stmt.var_def.data_type.is_array == False
    assert stmt.var_def.data_type.type_name.token_type == TokenType.INT_TYPE
    assert stmt.var_def.var_name.lexeme == 'g'
    assert stmt.expr.first.rvalue.path[2].var_name.lexeme == 'r'
    assert stmt.expr.op.token_type == TokenType.PLUS
    assert stmt.expr.rest.op.token_type == TokenType.MINUS
    assert stmt.expr.rest.rest.first.rvalue.path[1].var_name.lexeme == 'e'


#----------------------------------------------------------------------
# SEMANTIC CHECKER TEST CASES
#----------------------------------------------------------------------

def test_empty_table():
    table = SymbolTable()
    assert len(table) == 0

def test_push_pop():
    table = SymbolTable()
    assert len(table) == 0
    table.push_environment()
    assert len(table) == 1
    table.pop_environment()
    assert len(table) == 0
    table.push_environment()
    table.push_environment()    
    assert len(table) == 2
    table.pop_environment()
    assert len(table) == 1
    table.pop_environment()
    assert len(table) == 0

def test_simple_add():
    table = SymbolTable()
    table.add('x', 'int')
    assert not table.exists('x')
    table.push_environment()
    table.add('x', 'int')
    assert table.exists('x') and table.get('x') == 'int'
    table.pop_environment()

def test_multiple_add():
    table = SymbolTable()
    table.push_environment()
    table.add('x', 'int')
    table.add('y', 'double')
    assert table.exists('x') and table.get('x') == 'int'
    assert table.exists('y') and table.get('y') == 'double'

def test_multiple_environments():
    table = SymbolTable()
    table.push_environment()
    table.add('x', 'int')
    table.add('y', 'double')
    table.push_environment()
    table.add('x', 'string')
    table.add('z', 'bool')
    table.push_environment()
    table.add('u', 'Node')
    assert table.exists('x') and table.get('x') == 'string'
    assert table.exists('y') and table.get('y') == 'double'
    assert table.exists('z') and table.get('z') == 'bool'
    assert table.exists('u') and table.get('u') == 'Node'
    assert not table.exists_in_curr_env('x')
    assert not table.exists_in_curr_env('y')
    assert not table.exists_in_curr_env('z')
    assert table.exists_in_curr_env('u')
    table.pop_environment()
    assert not table.exists('u')
    assert table.exists_in_curr_env('x') and table.get('x') == 'string'
    assert table.exists_in_curr_env('z') and table.get('z') == 'bool'
    table.pop_environment()
    assert not table.exists('z')
    assert table.exists('x') and table.get('x') == 'int'
    assert table.exists('y') and table.get('y') == 'double'
    table.pop_environment()

    
#----------------------------------------------------------------------
# BASIC FUNCTION DEFINITIONS
#----------------------------------------------------------------------

def test_smallest_program():
    in_stream = FileWrapper(io.StringIO('void main() {}'))
    ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())

def test_valid_function_defs():
    in_stream = FileWrapper(io.StringIO(
        'void f1(int x) {} \n'
        'void f2(double x) {} \n'
        'bool f3(bool x) {} \n'
        'string f4(int p1, bool p2) {} \n'
        'void f5(double p1, int p2, string p3) {} \n'
        'int f6(int p1, int p2, string p3) {} \n'
        'array int f7() {} \n'
        'void main() {} \n'
    ))
    ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    
def test_missing_main():
    in_stream = FileWrapper(io.StringIO(''))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')

def test_main_with_bad_params():
    in_stream = FileWrapper(io.StringIO('void main(int x) {}'))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')

def test_main_with_bad_return_type():
    in_stream = FileWrapper(io.StringIO('int main() {}'))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')

def test_redefined_built_in():
    in_stream = FileWrapper(io.StringIO(
        'void input(string msg) {} \n'
        'void main() {} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')

def test_two_functions_same_name():
    in_stream = FileWrapper(io.StringIO(
        'void f(string msg) {} \n'
        'int f() {} \n'
        'void main() {} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')

def test_function_with_two_params_same_name():
    in_stream = FileWrapper(io.StringIO(
        'void f(int x, double y, string x) {} \n'
        'void main() {} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')

def test_function_with_bad_param_type():
    in_stream = FileWrapper(io.StringIO(
        'void f(int x, array double y, Node z) {} \n'
        'void main() {} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')

def test_function_with_bad_array_param_type():
    in_stream = FileWrapper(io.StringIO(
        'void f(int x, array Node y) {} \n'
        'void main() {} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')

def test_function_with_bad_return_type():
    in_stream = FileWrapper(io.StringIO(
        'Node f(int x) {} \n'
        'void main() {} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')
    
def test_function_with_bad_array_return_type():
    in_stream = FileWrapper(io.StringIO(
        'array Node f(int x) {} \n'
        'void main() {} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')

    
#------------------------------------------------------------
# BASIC STRUCT DEFINITION CASES
#------------------------------------------------------------

def test_valid_structs():
    in_stream = FileWrapper(io.StringIO(
        'struct S1 {int x; int y;} \n'
        'struct S2 {bool x; string y; double z;} \n'
        'struct S3 {S1 s1;} \n'
        'struct S4 {array int xs;} \n'
        'struct S5 {array S4 s4s;} \n'
        'void main() {} \n'
    ))
    ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())

def test_struct_self_ref():
    in_stream = FileWrapper(io.StringIO(
        'struct Node {int val; Node next;} \n'
        'struct BigNode {array int val; array Node children;} \n'
        'void main() {} \n'
    ))
    ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())

def test_struct_mutual_ref():
    in_stream = FileWrapper(io.StringIO(
        'struct S1 {int x; S2 y;} \n'
        'struct S2 {int u; S1 v;} \n'
        'void main() {} \n'
    ))
    ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())

def test_struct_and_function_same_name():
    in_stream = FileWrapper(io.StringIO(
        'struct s {} \n'
        'void s() {} \n'
        'void main() {} \n'
    ))
    ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())

def test_function_with_struct_param():
    in_stream = FileWrapper(io.StringIO(
        'void f(int x, S y, array S z) {} \n'
        'struct S {} \n'
        'void main() {} \n'
    ))
    ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())

def test_two_structs_same_name():
    in_stream = FileWrapper(io.StringIO(
        'struct S {int x;} \n'
        'struct S {bool y;} \n'
        'void main() {} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')

def test_struct_with_undefined_field_type():
    in_stream = FileWrapper(io.StringIO(
        'struct S1 {int x; S2 s;} \n'
        'void main() {} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')

def test_struct_with_same_field_names():
    in_stream = FileWrapper(io.StringIO(
        'struct S {int x; double y; string x;} \n'
        'void main() {} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')

    
#----------------------------------------------------------------------
# VARIABLE DECLARATIONS
#----------------------------------------------------------------------

def test_good_var_decls():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  int x1 = 0; \n'
        '  double x2 = 0.0; \n'
        '  bool x3 = false; \n'
        '  string x4 = "foo"; \n'
        '} \n'
    ))
    ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())    

def test_good_var_decls_with_null():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  int x1 = null; \n'
        '  double x2 = null; \n'
        '  bool x3 = null; \n'
        '  string x4 = null; \n'
        '} \n'
    ))
    ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())    

def test_good_var_decls_no_def():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  int x1; \n'
        '  double x2; \n'
        '  bool x3; \n'
        '  string x4; \n'
        '} \n'
    ))
    ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())    

def test_local_shadow(): 
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  int x1; \n'
        '  double x2; \n'
        '  bool x1; \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')

def test_mismatched_var_decl_types(): 
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  int x1 = 3.14; \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')

def test_mismatched_var_decl_array_types(): 
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  array int x1 = 256; \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')

    
#----------------------------------------------------------------------
# EXPRESSIONS
#----------------------------------------------------------------------

def test_expr_no_parens():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  int x1 = 1 + 2 + 3 * 4 / 5 - 6 - 7; \n'
        '  double x2 = 1.0 + 2.1 + 3.3 * 4.4 / 5.5 - 6.6 - 7.7; \n'
        '  bool x3 = not true or false and true and not false; \n'
        '  string x4 = "a" + "b" + "c"; \n'
        '} \n'
    ))
    ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())    
    
def test_expr_with_parens():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  int x1 = ((1 + 2) + (3 * 4)) / ((5 - 6) - 7); \n'
        '  double x2 = ((1.0 + 2.1) + (3.3 * 4.4) / (5.5 - 6.6)) - 7.7; \n'
        '  bool x3 = not (true or false) and (true and not false); \n'
        '  string x4 = (("a" + "b") + "c"); \n'
        '} \n'
    ))
    ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())    
    
def test_expr_with_parens_and_vars():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  int x1 = (1 + 2) + (3 * 4); \n'
        '  int x2 = (5 - 6) - 7; \n'
        '  int x3 = ((x1 / x2) + x1 - x2) / (x1 + x2); \n' 
        '  double x4 = (1.0 + 2.1) + (3.3 * 4.4); \n'
        '  double x5 = (5.5 - 6.6) - 7.7; \n'
        '  double x6 = ((x4 / x5) + x5 - x4) / (x4 + x5); \n'
        '  bool x7 = not (true or false); \n'
        '  bool x8 = true and not x7; \n'
        '  bool x9 = (x7 and x8) or (not x7 and x8) or (x7 and not x8); \n'
        '  string x10 = "a" + "b"; \n'
        '  string x11 = (x10 + "c") + ("c" + x10); \n'
        '} \n'
    ))
    ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())    

def test_basic_relational_ops():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  bool x1 = 0 < 1; \n'
        '  bool x2 = 0 <= 1; \n' 
        '  bool x3 = 0 > 1; \n'
        '  bool x4 = 0 >= 1; \n'
        '  bool x5 = 0 != 1; \n'
        '  bool x6 = 0 == 1; \n'
        '  bool x7 = 0 != null; \n'
        '  bool x8 = 0 == null; \n'
        '  bool x9 = null != null; \n'
        '  bool x10 = null == null; \n'
        '  bool x11 = not 0 < 1; \n'
        '} \n'
    ))
    ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())    

def test_combined_relational_ops():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  bool x1 = (0 < 1) and ("a" < "b") and (3.1 < 3.2); \n'
        '  bool x2 = (not ("a" == null)) or (not (3.1 != null)); \n'
        '  bool x4 = ("abc" <= "abde") or (x1 == false); \n'
        '  bool x5 = (not x2 == null) and 3.1 >= 4.1; \n'
        '} \n'
    ))
    ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())    
    
def test_array_comparisons():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  array int x1 = new int[10]; \n'
        '  array int x2 = x1; \n'
        '  bool x3 = (x2 != null) and ((x1 != x2) or (x1 == x2)); \n' 
        '} \n'
    ))
    ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())    

def test_bad_relational_comparison():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  bool x1 = (true < false); \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')
    
def test_bad_array_relational_comparison():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  array int x1 = new int[10]; \n'
        '  array int x2 = x1; \n'
        '  bool x1 = x1 <= x2; \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')

def test_bad_logical_negation():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  bool x = not (1 + 2); \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')


#----------------------------------------------------------------------
# FUNCTION RETURN TYPES
#----------------------------------------------------------------------

def test_function_return_match():
    in_stream = FileWrapper(io.StringIO(
        'int f() {return 42;} \n'
        'int g() {return null;} \n'
        'void h() {return null;} \n'
        'bool i() {return true;} \n'
        'array double j() {return new double[10];} \n'
        'void main() {} \n'
    ))
    ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())    

def test_bad_function_return_type():
    in_stream = FileWrapper(io.StringIO(
        'int f() {return true;} \n'
        'void main() { } \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')

def test_bad_non_null_return():
    in_stream = FileWrapper(io.StringIO(
        'void main() {return 0;} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')
    
def test_bad_one_return_bad_type():
    in_stream = FileWrapper(io.StringIO(
        'int f(int x) { \n'
        '  if (x < 0) {return 0;} \n'
        '  else {return false;} \n'
        '} \n'
        'void main() {} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')

    
#----------------------------------------------------------------------
# BASIC CONDITIONAL CHECKS
#----------------------------------------------------------------------

def test_bad_non_bool_if():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  if (1) {} \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')
    
def test_bad_non_bool_elseif():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  if (false) {} elseif ("a") {} \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')

def test_bad_bool_array_if():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  array bool flags = new bool[2]; \n'
        '  if (flags) {} \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')

def test_bad_bool_array_elseif():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  array bool flags = new bool[2]; \n'
        '  if (true) {} elseif (flags) {} \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')
    
def test_bad_bool_while():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  while (3 * 2) { } \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')

def test_bad_bool_array_while():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  bool xs = new bool[2]; \n'
        '  while (xs) { } \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')

def test_bad_bool_condition_for():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  for (int i; i + 1; i = i + 1) { } \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')

def test_bad_bool_condition_for_array():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  array bool xs = new bool[2]; \n'
        '  for (int i; xs; i = i + 1) { } \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')

    
#----------------------------------------------------------------------
# BASIC FUNCTION CALLS
#----------------------------------------------------------------------

def test_call_to_undeclared_function():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  f(); \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')

def test_too_few_args_in_function_call():
    in_stream = FileWrapper(io.StringIO(
        'void f(int x) {} \n'
        'void main() { \n'
        '  f(); \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')

def test_too_many_args_in_function_call():
    in_stream = FileWrapper(io.StringIO(
        'void f(int x) {} \n'
        'void main() { \n'
        '  f(1, 2); \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')
    

#----------------------------------------------------------------------
# SHADOWING
#----------------------------------------------------------------------

def test_allowed_shadowing():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  int x = 0; \n'
        '  if (true) { \n'
        '    double x = 1.0; \n'
        '    double y = x * 0.01; \n'
        '  } \n'
        '  elseif (false) { \n'
        '    bool x = true; \n'
        '    bool y = x and false; \n'
        '  } \n'
        '  for (double x = 0.0; x < 10.0; x = x + 1.0) { \n'
        '    double y = x / 2.0; \n'
        '  } \n'
        '  while (true) { \n'
        '    string x = ""; \n'
        '    string y = x + "a"; \n'
        '  } \n'        
        '} \n'
    ))
    ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())    
    
def test_illegal_shadowing_example():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  int x = 0; \n'
        '  if (true) { \n'
        '    int y = x  + 1; \n'
        '  } \n'
        '  double x = 1.0; \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')

    
#----------------------------------------------------------------------
# BUILT-IN FUNCTIONS
#----------------------------------------------------------------------

# print function

def test_print_exampes():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  print(0); \n'
        '  print(1.0); \n'
        '  print(true); \n'
        '  print("abc"); \n'
        '  int x = print(0); \n'  # print returns void
        '} \n'
    ))
    ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())    

def test_print_struct_object():
    in_stream = FileWrapper(io.StringIO(
        'struct S {} \n'
        'void main() { \n'
        '  S s = new S(); \n'
        '  print(s); \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')

def test_print_array_object():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  array int xs = new int[10]; \n'
        '  print(xs); \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')

def test_print_arg_mismatch():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  print(0, 1); \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')

# input function

def test_input_example():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  string s = input(); \n'
        '} \n'
    ))
    ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    
def test_input_return_mismatch():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  int s = input(); \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')
    
def test_input_too_many_args():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  int s = input("Name: "); \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')
    
# casting functions

def test_cast_examples():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  string x1 = itos(5); \n'
        '  string x2 = dtos(3.1); \n'
        '  int x3 = stoi("5"); \n'
        '  int x4 = dtoi(3.1); \n'
        '  double x5 = stod("3.1"); \n'
        '  double x6 = itod(5); \n'
        '} \n'
    ))
    ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    
# itos functions
    
def test_itos_too_few_args():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  string s = itos(); \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')
    
def test_itos_too_many_args():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  string s = itos(0, 1); \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')
    
def test_itos_bad_arg():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  string s = itos(1.0); \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')
    
def test_itos_bad_return():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  bool b = itos(1); \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')

# dtos function    

def test_dtos_too_few_args():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  string s = dtos(); \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')
    
def test_dtos_too_many_args():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  string s = dtos(0.0, 1.0); \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')
    
def test_dtos_bad_arg():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  string s = dtos(1); \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')

def test_dtos_bad_return():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  bool b = dtos(1.0); \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')

# itod function

def test_itod_too_few_args():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  double d = itod(); \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')
    
def test_itod_too_many_args():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  double d = itod(0, 1); \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')

def test_itod_bad_arg():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  double d = dtos(1); \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')
    
def test_itod_bad_return():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  bool b = itod(1); \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')

# dtoi function

def test_dtoi_too_few_args():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  int i = dtoi(); \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')
    
def test_dtoi_too_many_args():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  int i = dtoi(0.0, 1.0); \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')
    
def test_dtoi_bad_arg():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  int i = dtoi(1); \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')
    
def test_dtoi_bad_return():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  bool b = dtoi(1.0); \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')

# length function

def test_length_examples():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  int l1 = length("abc"); \n'
        '  int l2 = length(new int[1]); \n'
        '  int l3 = length(new double[10]); \n'
        '} \n'
    ))
    ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())

def test_length_too_few_args():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  int l = length(); \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')
    
def test_length_too_many_args():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  int l = length("abc", "def"); \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')

def test_length_bad_arg():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  int l = length(1.0); \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')
    
def test_length_bad_return():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  bool b = length("abc"); \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')

# get function

def test_get_examples():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  string c1 = get(0, "abc"); \n'
        '  string c2 = get(10, ""); \n'
        '} \n'
    ))
    ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())

def test_get_too_few_args():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  string c = get(0); \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')

def test_get_too_many_args():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  string c = get(0, "abc", "def"); \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')
    
def test_get_bad_first_arg():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  string c = get(1.0, "abc"); \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')
    
def test_get_bad_second_arg():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  string c = get(1, new string[10]); \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')
    
def test_get_bad_return():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  int i = get(0, "abc"); \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')
    
#------------------------------------------------------------
# USER-DEFINED FUNCTIONS CALLS
#------------------------------------------------------------

def test_single_parameter_call():
    in_stream = FileWrapper(io.StringIO(
        'int f(int x) {} \n'
        'void main() { \n'
        '  int x = f(1) + f(1 + 2); \n'
        '} \n'
    ))
    ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())

def test_bad_type_single_parameter_call():
    in_stream = FileWrapper(io.StringIO(
        'int f(int x) {} \n'
        'void main() { \n'
        '  int x = f(2.0); \n'
        '  int y = f(null); \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')

def test_bad_too_many_params_call():
    in_stream = FileWrapper(io.StringIO(
        'int f(int x) {} \n'
        'void main() { \n'
        '  int x = f(1, 2); \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')

def test_bad_too_few_params_call():
    in_stream = FileWrapper(io.StringIO(
        'int f(int x) {} \n'
        'void main() { \n'
        '  int x = f(); \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')
    
def test_bad_return_single_parameter_call():
    in_stream = FileWrapper(io.StringIO(
        'int f(int x) {} \n'
        'void main() { \n'
        '  double x = f(2); \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')
    
def test_mutiple_parameter_call():
    in_stream = FileWrapper(io.StringIO(
        'bool f(int x, double y, string z) {} \n'
        'void main() { \n'
        '  bool x = f(1, 2.0, "abc"); \n'
        '  bool y = f(null, null, null); \n'
        '} \n'
    ))
    ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())

def test_bad_arg_mutiple_parameter_call():
    in_stream = FileWrapper(io.StringIO(
        'int f(int x, double y, string z) {} \n'
        'void main() { \n'
        '  bool x = f(1, "abc", 2.0); \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')

def test_bad_return_mutiple_parameter_call():
    in_stream = FileWrapper(io.StringIO(
        'int f(int x, double y, string z) {} \n'
        'void main() { \n'
        '  string x = f(1, 2.0, "abc"); \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')
    
def test_bad_return_array_mutiple_parameter_call():
    in_stream = FileWrapper(io.StringIO(
        'array int f(int x, double y, string z) {} \n'
        'void main() { \n'
        '  int x = f(1, 2.0, "abc"); \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')

def test_bad_return_no_array_mutiple_parameter_call():
    in_stream = FileWrapper(io.StringIO(
        'int f(int x, double y, string z) {} \n'
        'void main() { \n'
        '  array int x = f(1, 2.0, "abc"); \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')

def test_single_param_access():
    in_stream = FileWrapper(io.StringIO(
        'int f(int x) {return x;} \n'
        'void main() { } \n'
    ))
    ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())

def test_multiple_param_access():
    in_stream = FileWrapper(io.StringIO(
        'double f(double x, double y) {return x + y;} \n'
        'void main() { } \n'
    ))
    ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())

def test_multiple_type_param_access():
    in_stream = FileWrapper(io.StringIO(
        'double f(double x, string y) {return x + stod(y);} \n'
        'void main() { } \n'
    ))
    ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())

def test_param_type_mismatch():
    in_stream = FileWrapper(io.StringIO(
        'double f(double x, string y) {return x + y;} \n'
        'void main() { } \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')

def test_missing_param():
    in_stream = FileWrapper(io.StringIO(
        'double f(double x) {return x + y;} \n'
        'void main() { } \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')

    
#----------------------------------------------------------------------
# ADDITIONAL ARRAY TESTS
#----------------------------------------------------------------------

def test_array_creation(): 
    in_stream = FileWrapper(io.StringIO(
        'struct S {} \n'
        'void main() { \n'
        '  int n = 10; \n'
        '  array int a1 = new int[n]; \n'
        '  array int a2 = null; \n'
        '  a2 = a1; \n'
        '  array double a3 = new double[10]; \n'
        '  array string a4 = new string[n+1]; \n'
        '  array string a5 = null; \n'
        '  array bool a6 = new bool[n]; \n'
        '  array S a7 = new S[n]; \n'
        '} \n'
    ))
    ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())

def test_bad_base_type_array_creation(): 
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  array int a1 = new double[n]; \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')

def test_bad_struct_type_array_creation(): 
    in_stream = FileWrapper(io.StringIO(
        'struct S1 {} \n'
        'struct S2 {} \n'
        'void main() { \n'
        '  array S1 a1 = new S2[n]; \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')

def test_array_access():
    in_stream = FileWrapper(io.StringIO(
        'struct S1 {string val;} \n'
        'void main() { \n'
        '  int n = 10; \n'
        '  array bool a1 = new bool[n]; \n'
        '  array S1 a2 = new S1[n]; \n'
        '  bool x = a1[n-5]; \n'
        '  a1[0] = x or true; \n'
        '  a2[0] = null; \n'
        '  S1 s = a2[1]; \n'
        '  string t = a2[0].val; \n'
        '} \n'
    ))
    ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    
def test_bad_array_assignment(): 
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  array bool a1 = new bool[10]; \n'
        '  a1[0] = 10; \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')

def test_bad_array_access(): 
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  array bool a1 = new bool[10]; \n'
        '  int x = a1[0]; \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')
    
    
#----------------------------------------------------------------------
# ADDITIONAL STRUCT TESTS
#----------------------------------------------------------------------

def test_struct_creation():
    in_stream = FileWrapper(io.StringIO(
        'struct S1 { } \n'
        'struct S2 {int x;} \n'
        'struct S3 {int x; string y;} \n'
        'void main() { \n'
        '  S1 p1 = new S1(); \n'
        '  S2 p2 = new S2(5); \n'
        '  S3 p3 = new S3(5, "a"); \n'
        '  S3 p4 = new S3(null, null); \n'
        '} \n'
    ))
    ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())

def test_bad_struct_creation_too_few_args():
    in_stream = FileWrapper(io.StringIO(
        'struct S1 {int x;} \n'
        'void main() { \n'
        '  S1 p1 = new S1(); \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')

def test_bad_struct_creation_too_many_args():
    in_stream = FileWrapper(io.StringIO(
        'struct S1 {int x;} \n'
        'void main() { \n'
        '  S1 p1 = new S1(1, 2); \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')

def test_bad_struct_creation_bad_arg_type():
    in_stream = FileWrapper(io.StringIO(
        'struct S1 {int x; string y;} \n'
        'void main() { \n'
        '  S1 p1 = new S1(1, 2); \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')

def test_struct_path_examples():
    in_stream = FileWrapper(io.StringIO(
        'struct S {double val; T t;} \n'
        'struct T {bool val; S s;} \n'
        'void main() { \n'
        '  S s; \n'
        '  T t = new T(null, s); \n'
        '  s = new S(null, t); \n'
        '  s.val = 1.0; \n'
        '  t.val = true; \n'
        '  s.t.val = false; \n'
        '  t.s.val = 2.0; \n'
        '  s.t.s.val = 3.0; \n'
        '  t.s.t.val = true; \n'
        '  double x = s.val; \n'
        '  bool y = t.val; \n'
        '  y = s.t.val; \n'
        '  x = t.s.val; \n'
        '  x = s.t.s.val; \n'
        '  y = t.s.t.val; \n'
        '} \n'
    ))
    ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    
def test_bad_lvalue_path_type(): 
    in_stream = FileWrapper(io.StringIO(
        'struct S1 {double val; S1 s;} \n'
        'void main() { \n'
        '  S1 p = new S1(null, null); \n'
        '  s.s.val = 0; \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')


def test_bad_rvalue_path_type(): 
    in_stream = FileWrapper(io.StringIO(
        'struct S1 {double val; S1 s;} \n'
        'void main() { \n'
        '  S1 p = new S1(null, null); \n'
        '  int x = p.s.s.val; \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')

def test_lvalue_array_path_type(): 
    in_stream = FileWrapper(io.StringIO(
        'struct S1 {double val; array S1 s;} \n'
        'void main() { \n'
        '  S1 p = new S1(null, null); \n'
        '  p.s[0].s[1].val = 5.0; \n'
        '} \n'
    ))
    ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    
def test_bad_lvalue_array_path_type(): 
    in_stream = FileWrapper(io.StringIO(
        'struct S1 {double val; array S1 s;} \n'
        'void main() { \n'
        '  S1 p = new S1(null, null); \n'
        '  p.s[0].s.val = 5.0; \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')

    
#----------------------------------------------------------------------
# TODO: Add at least 10 of your own tests below. Half of the tests
# should be positive tests, and half should be negative. Focus on
# trickier parts of your code (e.g., rvalues, lvalues, new rvalues)
# looking for places in your code that are not tested by the above.
#----------------------------------------------------------------------

# POSITIVE TESTS
def test_path_type_both_sides():
    in_stream = FileWrapper(io.StringIO(
        'struct S1 {double val; array S1 s;} \n'
        'void main() { \n'
        '  S1 p = new S1(null, null); \n'
        '  p.s[4].s[45].s[6].val = p.s[8].s[33].s[7].val; \n'
        '} \n'
    ))
    ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())

def test_nested_structs_path():
    in_stream = FileWrapper(io.StringIO(
        'struct S1 {double r; array S1 s;} \n'
        'struct S2 {int z; S1 x;} \n'
        'struct S3 {string l; S2 h;} \n'
        'void main() { \n'
        '  S3 p = new S3(null, null); \n'
        '  S1 new_s = p.h.x.s[0]; \n'
        '} \n'
    ))
    ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())

def test_path_in_function_call():
    in_stream = FileWrapper(io.StringIO(
        'struct S1 {double val; array S1 s;} \n'
        'void main() { \n'
        '  S1 p = new S1(null, null); \n'
        '  string x = dtos(p.s[8].s[33].s[7].s[6].val); \n'
        '} \n'
    ))
    ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())

def test_struct_creation_with_array_creation():
    in_stream = FileWrapper(io.StringIO(
        'struct S1 {double val; array S1 s;} \n'
        'void main() { \n'
        '  S1 p = new S1(null, null); \n'
        '  S1 different = new S1(3.25, new S1[45]);'
        '} \n'
    ))
    ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())

def test_array_creation_with_expr():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  array int z = new int[7+8+3-2-6*8*9]; \n'
        '  string l = "8";'
        '  array double x = new double[stoi(l)];'
        '} \n'
    ))
    ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())

# NEGATIVE TESTS
def test_bad_path_type_both_sides():
    in_stream = FileWrapper(io.StringIO(
        'struct S1 {double val; array S1 s;} \n'
        'void main() { \n'
        '  S1 p = new S1(null, null); \n'
        '  p.s[4].s[45].s[6].val = p.s[8].s[33].s[7].s[6]; \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')

def test_bad_array_reference_expr():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  array int A = new int[40]; \n'
        '  int x = A[3.2-8]; \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')

def test_array_creation_with_bad_declaration():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  array int A = new int[40]; \n'
        '  array double bad = new string[30]; \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')

def test_struct_creation_with_bad_call_expr():
    in_stream = FileWrapper(io.StringIO(
        'struct S1 {double val; int z;} \n'
        'void main() { \n'
        '  S1 good_struct = new S1(2.3345, 2); \n'
        '  int z = 2;'
        '  S1 bad_struct = new S1(4.3223, itos(z)); \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')

def test_bad_path_in_call_expr():
    in_stream = FileWrapper(io.StringIO(
        'struct S1 {double val; array S1 s;} \n'
        'void main() { \n'
        '  S1 p = new S1(null, null); \n'
        '  double x = dtos(p.s[8].s[33].s[7].s[6].val); \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')

#----------------------------------------------------------------------
# OP CODE TEST CASES
#----------------------------------------------------------------------

def test_single_nop():
    main = VMFrameTemplate('main', 0)
    main.instructions.append(NOP())
    vm = VM()
    vm.add_frame_template(main)
    vm.run()

def test_single_write(capsys):
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH('blue'))
    main.instructions.append(WRITE())
    vm = VM()
    vm.add_frame_template(main)
    vm.run()
    captured = capsys.readouterr()
    assert captured.out == 'blue'


def test_dup(capsys):
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(24))
    main.instructions.append(DUP())
    main.instructions.append(WRITE())
    main.instructions.append(WRITE())    
    vm = VM()
    vm.add_frame_template(main)
    vm.run()
    captured = capsys.readouterr()
    assert captured.out == '2424'
    
#----------------------------------------------------------------------
# BASIC LITERALS AND VARIABLES
#----------------------------------------------------------------------

def test_single_pop(capsys):
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH('blue'))
    main.instructions.append(PUSH('green'))
    main.instructions.append(POP())
    main.instructions.append(WRITE())
    vm = VM()
    vm.add_frame_template(main)
    vm.run()
    captured = capsys.readouterr()
    assert captured.out == 'blue'
    
def test_write_null(capsys):
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(None))
    main.instructions.append(WRITE())
    vm = VM()
    vm.add_frame_template(main)
    vm.run()
    captured = capsys.readouterr()
    assert captured.out == 'null'

def test_store_and_load(capsys):
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH('blue'))
    main.instructions.append(STORE(0))
    main.instructions.append(LOAD(0))
    main.instructions.append(WRITE())
    vm = VM()
    vm.add_frame_template(main)
    vm.run()
    captured = capsys.readouterr()
    assert captured.out == 'blue'
    
#----------------------------------------------------------------------
# OPERATIONS
#----------------------------------------------------------------------

def test_int_add(capsys):
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(12))
    main.instructions.append(PUSH(24))
    main.instructions.append(ADD())
    main.instructions.append(WRITE())
    vm = VM()
    vm.add_frame_template(main)
    vm.run()
    captured = capsys.readouterr()
    assert captured.out == '36'

def test_double_add(capsys):
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(3.50))
    main.instructions.append(PUSH(2.25))
    main.instructions.append(ADD())
    main.instructions.append(WRITE())
    vm = VM()
    vm.add_frame_template(main)
    vm.run()
    captured = capsys.readouterr()
    assert captured.out == '5.75'

def test_string_add(capsys):
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH('abc'))
    main.instructions.append(PUSH('def'))
    main.instructions.append(ADD())
    main.instructions.append(WRITE())
    vm = VM()
    vm.add_frame_template(main)
    vm.run()
    captured = capsys.readouterr()
    assert captured.out == 'abcdef'

def test_null_add_first_operand():
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(None))
    main.instructions.append(PUSH(24))
    main.instructions.append(ADD())
    vm = VM()
    vm.add_frame_template(main)
    with pytest.raises(MyPLError) as e:
        vm.run()
    assert str(e.value).startswith('VM Error:')
    
def test_null_add_second_operand():
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(12))
    main.instructions.append(PUSH(None))
    main.instructions.append(ADD())
    vm = VM()
    vm.add_frame_template(main)
    with pytest.raises(MyPLError) as e:
        vm.run()
    assert str(e.value).startswith('VM Error:')

def test_int_sub(capsys):
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(15))
    main.instructions.append(PUSH(9))
    main.instructions.append(SUB())
    main.instructions.append(WRITE())
    vm = VM()
    vm.add_frame_template(main)
    vm.run()
    captured = capsys.readouterr()
    assert captured.out == '6'

def test_double_sub(capsys):
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(3.75))
    main.instructions.append(PUSH(2.50))
    main.instructions.append(SUB())
    main.instructions.append(WRITE())
    vm = VM()
    vm.add_frame_template(main)
    vm.run()
    captured = capsys.readouterr()
    assert captured.out == '1.25'
    
def test_null_sub_first_operand():
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(None))
    main.instructions.append(PUSH(10))
    main.instructions.append(SUB())
    vm = VM()
    vm.add_frame_template(main)
    with pytest.raises(MyPLError) as e:
        vm.run()
    assert str(e.value).startswith('VM Error:')

def test_null_sub_second_operand():
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(10))
    main.instructions.append(PUSH(None))
    main.instructions.append(SUB())
    vm = VM()
    vm.add_frame_template(main)
    with pytest.raises(MyPLError) as e:
        vm.run()
    assert str(e.value).startswith('VM Error:')

def test_int_mult(capsys):
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(15))
    main.instructions.append(PUSH(3))
    main.instructions.append(MUL())
    main.instructions.append(WRITE())
    vm = VM()
    vm.add_frame_template(main)
    vm.run()
    captured = capsys.readouterr()
    assert captured.out == '45'

def test_double_mult(capsys):
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(1.25))
    main.instructions.append(PUSH(3.00))
    main.instructions.append(MUL())
    main.instructions.append(WRITE())
    vm = VM()
    vm.add_frame_template(main)
    vm.run()
    captured = capsys.readouterr()
    assert captured.out == '3.75'
    
def test_null_mult_first_operand():
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(None))
    main.instructions.append(PUSH(10))
    main.instructions.append(MUL())
    vm = VM()
    vm.add_frame_template(main)
    with pytest.raises(MyPLError) as e:
        vm.run()
    assert str(e.value).startswith('VM Error:')

def test_null_mult_second_operand():
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(10))
    main.instructions.append(PUSH(None))
    main.instructions.append(MUL())
    vm = VM()
    vm.add_frame_template(main)
    with pytest.raises(MyPLError) as e:
        vm.run()
    assert str(e.value).startswith('VM Error:')

def test_int_div(capsys):
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(16))
    main.instructions.append(PUSH(3))
    main.instructions.append(DIV())
    main.instructions.append(WRITE())
    vm = VM()
    vm.add_frame_template(main)
    vm.run()
    captured = capsys.readouterr()
    assert captured.out == '5'

def test_bad_int_div_by_zero():
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(10))
    main.instructions.append(PUSH(0))
    main.instructions.append(DIV())
    vm = VM()
    vm.add_frame_template(main)
    with pytest.raises(MyPLError) as e:
        vm.run()
    assert str(e.value).startswith('VM Error:')
    
def test_double_div(capsys):
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(3.75))
    main.instructions.append(PUSH(3.00))
    main.instructions.append(DIV())
    main.instructions.append(WRITE())
    vm = VM()
    vm.add_frame_template(main)
    vm.run()
    captured = capsys.readouterr()
    assert captured.out == '1.25'

def test_bad_double_div_by_zero():
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(10.0))
    main.instructions.append(PUSH(0.0))
    main.instructions.append(DIV())
    vm = VM()
    vm.add_frame_template(main)
    with pytest.raises(MyPLError) as e:
        vm.run()
    assert str(e.value).startswith('VM Error:')
    
def test_null_div_first_operand():
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(None))
    main.instructions.append(PUSH(10))
    main.instructions.append(DIV())
    vm = VM()
    vm.add_frame_template(main)
    with pytest.raises(MyPLError) as e:
        vm.run()
    assert str(e.value).startswith('VM Error:')

def test_null_div_second_operand():
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(10))
    main.instructions.append(PUSH(None))
    main.instructions.append(DIV())
    vm = VM()
    vm.add_frame_template(main)
    with pytest.raises(MyPLError) as e:
        vm.run()
    assert str(e.value).startswith('VM Error:')
    
def test_and(capsys):
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(True))
    main.instructions.append(PUSH(True))
    main.instructions.append(AND())
    main.instructions.append(PUSH(False))
    main.instructions.append(PUSH(True))
    main.instructions.append(AND())
    main.instructions.append(PUSH(True))
    main.instructions.append(PUSH(False))
    main.instructions.append(AND())
    main.instructions.append(PUSH(False))
    main.instructions.append(PUSH(False))
    main.instructions.append(AND())
    main.instructions.append(WRITE())    
    main.instructions.append(WRITE())
    main.instructions.append(WRITE())
    main.instructions.append(WRITE())        
    vm = VM()
    vm.add_frame_template(main)
    vm.run()
    captured = capsys.readouterr()
    assert captured.out == 'falsefalsefalsetrue'
    
def test_null_and_first_operand():
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(None))
    main.instructions.append(PUSH(True))
    main.instructions.append(AND())
    vm = VM()
    vm.add_frame_template(main)
    with pytest.raises(MyPLError) as e:
        vm.run()
    assert str(e.value).startswith('VM Error:')

def test_null_and_second_operand():
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(False))
    main.instructions.append(PUSH(None))
    main.instructions.append(AND())
    vm = VM()
    vm.add_frame_template(main)
    with pytest.raises(MyPLError) as e:
        vm.run()
    assert str(e.value).startswith('VM Error:')

def test_or(capsys):
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(True))
    main.instructions.append(PUSH(True))
    main.instructions.append(OR())
    main.instructions.append(PUSH(False))
    main.instructions.append(PUSH(True))
    main.instructions.append(OR())
    main.instructions.append(PUSH(True))
    main.instructions.append(PUSH(False))
    main.instructions.append(OR())
    main.instructions.append(PUSH(False))
    main.instructions.append(PUSH(False))
    main.instructions.append(OR())
    main.instructions.append(WRITE())    
    main.instructions.append(WRITE())
    main.instructions.append(WRITE())
    main.instructions.append(WRITE())        
    vm = VM()
    vm.add_frame_template(main)
    vm.run()
    captured = capsys.readouterr()
    assert captured.out == 'falsetruetruetrue'
    
def test_null_or_first_operand():
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(None))
    main.instructions.append(PUSH(True))
    main.instructions.append(OR())
    vm = VM()
    vm.add_frame_template(main)
    with pytest.raises(MyPLError) as e:
        vm.run()
    assert str(e.value).startswith('VM Error:')

def test_null_or_second_operand():
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(False))
    main.instructions.append(PUSH(None))
    main.instructions.append(OR())
    vm = VM()
    vm.add_frame_template(main)
    with pytest.raises(MyPLError) as e:
        vm.run()
    assert str(e.value).startswith('VM Error:')

def test_not(capsys):
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(True))
    main.instructions.append(NOT())
    main.instructions.append(PUSH(False))
    main.instructions.append(NOT())
    main.instructions.append(WRITE())    
    main.instructions.append(WRITE())
    vm = VM()
    vm.add_frame_template(main)
    vm.run()
    captured = capsys.readouterr()
    assert captured.out == 'truefalse'
    
def test_null_not_operand():
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(None))
    main.instructions.append(NOT())
    vm = VM()
    vm.add_frame_template(main)
    with pytest.raises(MyPLError) as e:
        vm.run()
    assert str(e.value).startswith('VM Error:')

def test_int_less_than(capsys):
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(1))
    main.instructions.append(PUSH(2))
    main.instructions.append(CMPLT())
    main.instructions.append(PUSH(2))
    main.instructions.append(PUSH(1))
    main.instructions.append(CMPLT())
    main.instructions.append(PUSH(2))
    main.instructions.append(PUSH(2))
    main.instructions.append(CMPLT())
    main.instructions.append(WRITE())    
    main.instructions.append(WRITE())
    main.instructions.append(WRITE())
    vm = VM()
    vm.add_frame_template(main)
    vm.run()
    captured = capsys.readouterr()
    assert captured.out == 'falsefalsetrue'

def test_double_less_than(capsys):
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(1.25))
    main.instructions.append(PUSH(1.50))
    main.instructions.append(CMPLT())
    main.instructions.append(PUSH(1.50))
    main.instructions.append(PUSH(1.25))
    main.instructions.append(CMPLT())
    main.instructions.append(PUSH(2.125))
    main.instructions.append(PUSH(2.125))
    main.instructions.append(CMPLT())
    main.instructions.append(WRITE())    
    main.instructions.append(WRITE())
    main.instructions.append(WRITE())
    vm = VM()
    vm.add_frame_template(main)
    vm.run()
    captured = capsys.readouterr()
    assert captured.out == 'falsefalsetrue'

def test_string_less_than(capsys):
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH('abc'))
    main.instructions.append(PUSH('abd'))
    main.instructions.append(CMPLT())
    main.instructions.append(PUSH('abd'))
    main.instructions.append(PUSH('abc'))
    main.instructions.append(CMPLT())
    main.instructions.append(PUSH('abc'))
    main.instructions.append(PUSH('abc'))
    main.instructions.append(CMPLT())
    main.instructions.append(WRITE())    
    main.instructions.append(WRITE())
    main.instructions.append(WRITE())
    vm = VM()
    vm.add_frame_template(main)
    vm.run()
    captured = capsys.readouterr()
    assert captured.out == 'falsefalsetrue'

def test_less_than_null_first_operand():
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(None))
    main.instructions.append(PUSH(1))
    main.instructions.append(CMPLT())
    vm = VM()
    vm.add_frame_template(main)
    with pytest.raises(MyPLError) as e:
        vm.run()
    assert str(e.value).startswith('VM Error:')

def test_less_than_null_second_operand():
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(1))
    main.instructions.append(PUSH(None))
    main.instructions.append(CMPLT())
    vm = VM()
    vm.add_frame_template(main)
    with pytest.raises(MyPLError) as e:
        vm.run()
    assert str(e.value).startswith('VM Error:')

def test_int_less_than_equal(capsys):
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(1))
    main.instructions.append(PUSH(2))
    main.instructions.append(CMPLE())
    main.instructions.append(PUSH(2))
    main.instructions.append(PUSH(1))
    main.instructions.append(CMPLE())
    main.instructions.append(PUSH(2))
    main.instructions.append(PUSH(2))
    main.instructions.append(CMPLE())
    main.instructions.append(WRITE())    
    main.instructions.append(WRITE())
    main.instructions.append(WRITE())
    vm = VM()
    vm.add_frame_template(main)
    vm.run()
    captured = capsys.readouterr()
    assert captured.out == 'truefalsetrue'

def test_double_less_than_equal(capsys):
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(1.25))
    main.instructions.append(PUSH(1.50))
    main.instructions.append(CMPLE())
    main.instructions.append(PUSH(1.50))
    main.instructions.append(PUSH(1.25))
    main.instructions.append(CMPLE())
    main.instructions.append(PUSH(2.125))
    main.instructions.append(PUSH(2.125))
    main.instructions.append(CMPLE())
    main.instructions.append(WRITE())    
    main.instructions.append(WRITE())
    main.instructions.append(WRITE())
    vm = VM()
    vm.add_frame_template(main)
    vm.run()
    captured = capsys.readouterr()
    assert captured.out == 'truefalsetrue'

def test_string_less_than_equal(capsys):
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH('abc'))
    main.instructions.append(PUSH('abd'))
    main.instructions.append(CMPLE())
    main.instructions.append(PUSH('abd'))
    main.instructions.append(PUSH('abc'))
    main.instructions.append(CMPLE())
    main.instructions.append(PUSH('abc'))
    main.instructions.append(PUSH('abc'))
    main.instructions.append(CMPLE())
    main.instructions.append(WRITE())    
    main.instructions.append(WRITE())
    main.instructions.append(WRITE())
    vm = VM()
    vm.add_frame_template(main)
    vm.run()
    captured = capsys.readouterr()
    assert captured.out == 'truefalsetrue'

def test_less_than_equal_null_first_operand():
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(None))
    main.instructions.append(PUSH(1))
    main.instructions.append(CMPLE())
    vm = VM()
    vm.add_frame_template(main)
    with pytest.raises(MyPLError) as e:
        vm.run()
    assert str(e.value).startswith('VM Error:')

def test_less_than_equal_null_second_operand():
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(1))
    main.instructions.append(PUSH(None))
    main.instructions.append(CMPLE())
    vm = VM()
    vm.add_frame_template(main)
    with pytest.raises(MyPLError) as e:
        vm.run()
    assert str(e.value).startswith('VM Error:')

def test_int_equal(capsys):
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(1))
    main.instructions.append(PUSH(2))
    main.instructions.append(CMPEQ())
    main.instructions.append(PUSH(2))
    main.instructions.append(PUSH(1))
    main.instructions.append(CMPEQ())
    main.instructions.append(PUSH(2))
    main.instructions.append(PUSH(2))
    main.instructions.append(CMPEQ())
    main.instructions.append(WRITE())    
    main.instructions.append(WRITE())
    main.instructions.append(WRITE())
    vm = VM()
    vm.add_frame_template(main)
    vm.run()
    captured = capsys.readouterr()
    assert captured.out == 'truefalsefalse'

def test_double_equal(capsys):
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(1.25))
    main.instructions.append(PUSH(1.50))
    main.instructions.append(CMPEQ())
    main.instructions.append(PUSH(1.50))
    main.instructions.append(PUSH(1.25))
    main.instructions.append(CMPEQ())
    main.instructions.append(PUSH(2.125))
    main.instructions.append(PUSH(2.125))
    main.instructions.append(CMPEQ())
    main.instructions.append(WRITE())    
    main.instructions.append(WRITE())
    main.instructions.append(WRITE())
    vm = VM()
    vm.add_frame_template(main)
    vm.run()
    captured = capsys.readouterr()
    assert captured.out == 'truefalsefalse'

def test_string_equal(capsys):
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH('abc'))
    main.instructions.append(PUSH('abd'))
    main.instructions.append(CMPEQ())
    main.instructions.append(PUSH('abd'))
    main.instructions.append(PUSH('abc'))
    main.instructions.append(CMPEQ())
    main.instructions.append(PUSH('abc'))
    main.instructions.append(PUSH('abc'))
    main.instructions.append(CMPEQ())
    main.instructions.append(WRITE())    
    main.instructions.append(WRITE())
    main.instructions.append(WRITE())
    vm = VM()
    vm.add_frame_template(main)
    vm.run()
    captured = capsys.readouterr()
    assert captured.out == 'truefalsefalse'

def test_equal_null_first_operand(capsys):
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(None))
    main.instructions.append(PUSH(1))
    main.instructions.append(CMPEQ())
    main.instructions.append(WRITE())
    vm = VM()
    vm.add_frame_template(main)
    vm.run()
    captured = capsys.readouterr()
    assert captured.out == 'false'

def test_equal_null_second_operand(capsys):
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(1))
    main.instructions.append(PUSH(None))
    main.instructions.append(CMPEQ())
    main.instructions.append(WRITE())
    vm = VM()
    vm.add_frame_template(main)
    vm.run()
    captured = capsys.readouterr()
    assert captured.out == 'false'

def test_int_not_equal(capsys):
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(1))
    main.instructions.append(PUSH(2))
    main.instructions.append(CMPNE())
    main.instructions.append(PUSH(2))
    main.instructions.append(PUSH(1))
    main.instructions.append(CMPNE())
    main.instructions.append(PUSH(2))
    main.instructions.append(PUSH(2))
    main.instructions.append(CMPNE())
    main.instructions.append(WRITE())    
    main.instructions.append(WRITE())
    main.instructions.append(WRITE())
    vm = VM()
    vm.add_frame_template(main)
    vm.run()
    captured = capsys.readouterr()
    assert captured.out == 'falsetruetrue'

def test_double_not_equal(capsys):
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(1.25))
    main.instructions.append(PUSH(1.50))
    main.instructions.append(CMPNE())
    main.instructions.append(PUSH(1.50))
    main.instructions.append(PUSH(1.25))
    main.instructions.append(CMPNE())
    main.instructions.append(PUSH(2.125))
    main.instructions.append(PUSH(2.125))
    main.instructions.append(CMPNE())
    main.instructions.append(WRITE())    
    main.instructions.append(WRITE())
    main.instructions.append(WRITE())
    vm = VM()
    vm.add_frame_template(main)
    vm.run()
    captured = capsys.readouterr()
    assert captured.out == 'falsetruetrue'

def test_string_not_equal(capsys):
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH('abc'))
    main.instructions.append(PUSH('abd'))
    main.instructions.append(CMPNE())
    main.instructions.append(PUSH('abd'))
    main.instructions.append(PUSH('abc'))
    main.instructions.append(CMPNE())
    main.instructions.append(PUSH('abc'))
    main.instructions.append(PUSH('abc'))
    main.instructions.append(CMPNE())
    main.instructions.append(WRITE())    
    main.instructions.append(WRITE())
    main.instructions.append(WRITE())
    vm = VM()
    vm.add_frame_template(main)
    vm.run()
    captured = capsys.readouterr()
    assert captured.out == 'falsetruetrue'

def test_not_equal_null_first_operand(capsys):
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(None))
    main.instructions.append(PUSH(1))
    main.instructions.append(CMPNE())
    main.instructions.append(WRITE())
    vm = VM()
    vm.add_frame_template(main)
    vm.run()
    captured = capsys.readouterr()
    assert captured.out == 'true'

def test_not_equal_null_second_operand(capsys):
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(1))
    main.instructions.append(PUSH(None))
    main.instructions.append(CMPNE())
    main.instructions.append(WRITE())
    vm = VM()
    vm.add_frame_template(main)
    vm.run()
    captured = capsys.readouterr()
    assert captured.out == 'true'

    
#----------------------------------------------------------------------
# Jumps
#----------------------------------------------------------------------

def test_jump_forward(capsys):
    main = VMFrameTemplate('main', 0)
    main.instructions.append(JMP(3))
    main.instructions.append(PUSH('blue'))
    main.instructions.append(WRITE())
    main.instructions.append(PUSH('green'))
    main.instructions.append(WRITE())
    vm = VM()
    vm.add_frame_template(main)
    vm.run()
    captured = capsys.readouterr()
    assert captured.out == 'green'

                
def test_jump_false_forward(capsys):
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(False))
    main.instructions.append(JMPF(4))
    main.instructions.append(PUSH('blue'))
    main.instructions.append(WRITE())
    main.instructions.append(PUSH('green'))
    main.instructions.append(WRITE())
    vm = VM()
    vm.add_frame_template(main)
    vm.run()
    captured = capsys.readouterr()
    assert captured.out == 'green'

def test_jump_false_no_jump(capsys):
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(True))
    main.instructions.append(JMPF(4))
    main.instructions.append(PUSH('blue'))
    main.instructions.append(WRITE())
    main.instructions.append(PUSH('green'))
    main.instructions.append(WRITE())
    vm = VM()
    vm.add_frame_template(main)
    vm.run()
    captured = capsys.readouterr()
    assert captured.out == 'bluegreen'

def test_jump_backwards(capsys):
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(0))       # 0
    main.instructions.append(STORE(0))      # 1
    main.instructions.append(LOAD(0))       # 2
    main.instructions.append(PUSH(2))       # 3
    main.instructions.append(CMPLT())       # 4
    main.instructions.append(JMPF(13))      # 5
    main.instructions.append(PUSH('blue'))  # 6
    main.instructions.append(WRITE())       # 7
    main.instructions.append(LOAD(0))       # 8
    main.instructions.append(PUSH(1))       # 9
    main.instructions.append(ADD())         # 10
    main.instructions.append(STORE(0))      # 11
    main.instructions.append(JMP(2))        # 12
    main.instructions.append(PUSH('green')) # 13
    main.instructions.append(WRITE())       # 14
    vm = VM()
    vm.add_frame_template(main)
    vm.run()
    captured = capsys.readouterr()
    assert captured.out == 'bluebluegreen'

#----------------------------------------------------------------------
# FUNCTIONS
#----------------------------------------------------------------------

def test_main_returns_null(capsys):
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(None))
    main.instructions.append(RET())
    vm = VM()
    vm.add_frame_template(main)
    vm.run()


def test_function_returns_literal(capsys):
    f = VMFrameTemplate('f', 0)
    f.instructions.append(PUSH('blue'))
    f.instructions.append(RET())
    main = VMFrameTemplate('main', 0)
    main.instructions.append(CALL('f'))
    main.instructions.append(WRITE())
    vm = VM()
    vm.add_frame_template(f)
    vm.add_frame_template(main)
    vm.run()
    captured = capsys.readouterr()
    assert captured.out == 'blue'

def test_function_returns_modified_param(capsys):
    f = VMFrameTemplate('f', 1)
    f.instructions.append(PUSH(4))
    f.instructions.append(ADD())
    f.instructions.append(RET())
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(3))
    main.instructions.append(CALL('f'))
    main.instructions.append(WRITE())
    vm = VM()
    vm.add_frame_template(f)
    vm.add_frame_template(main)
    vm.run()
    captured = capsys.readouterr()
    assert captured.out == '7'

def test_function_two_params_subtracted(capsys):
    f = VMFrameTemplate('f', 2)
    f.instructions.append(STORE(0))
    f.instructions.append(STORE(1))
    f.instructions.append(LOAD(0))
    f.instructions.append(LOAD(1))
    f.instructions.append(SUB())
    f.instructions.append(RET())
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(4))
    main.instructions.append(PUSH(3))    
    main.instructions.append(CALL('f'))
    main.instructions.append(WRITE())
    vm = VM()
    vm.add_frame_template(f)
    vm.add_frame_template(main)
    vm.run()
    captured = capsys.readouterr()
    assert captured.out == '1'

def test_function_two_params_printed(capsys):
    f = VMFrameTemplate('f', 2)
    f.instructions.append(STORE(0))
    f.instructions.append(STORE(1))
    f.instructions.append(LOAD(0))
    f.instructions.append(WRITE())
    f.instructions.append(LOAD(1))
    f.instructions.append(WRITE())
    f.instructions.append(PUSH(None))        # return null
    f.instructions.append(RET())
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH('blue'))
    main.instructions.append(PUSH('green'))    
    main.instructions.append(CALL('f'))
    main.instructions.append(POP())          # clean up return value
    vm = VM()
    vm.add_frame_template(f)
    vm.add_frame_template(main)
    vm.run()
    captured = capsys.readouterr()
    assert captured.out == 'bluegreen'

def test_function_recursive_sum_function(capsys):
    f = VMFrameTemplate('sum', 1)
    f.instructions.append(STORE(0))    # x -> var[0]
    f.instructions.append(LOAD(0))     # push x
    f.instructions.append(PUSH(0))     # push 0
    f.instructions.append(CMPLE())     # x < 0
    f.instructions.append(JMPF(7))  
    f.instructions.append(PUSH(0))
    f.instructions.append(RET())       # return 0
    f.instructions.append(LOAD(0))     # push x
    f.instructions.append(PUSH(1))
    f.instructions.append(SUB())       # x - 1
    f.instructions.append(CALL('sum')) # sum(x-1)
    f.instructions.append(LOAD(0))     # push x
    f.instructions.append(ADD())       # sum(x-1) + x
    f.instructions.append(RET())       # return sum(x-1) + x    
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(4))
    main.instructions.append(CALL('sum'))
    main.instructions.append(WRITE())
    vm = VM()
    vm.add_frame_template(f)
    vm.add_frame_template(main)
    vm.run()
    captured = capsys.readouterr()
    assert captured.out == '10'

def test_call_multiple_functions(capsys):
    # int f(int x) { return g(x+1) + 1; }
    f = VMFrameTemplate('f', 1)
    f.instructions.append(STORE(0))    # x -> var[0]
    f.instructions.append(LOAD(0))     # push x
    f.instructions.append(PUSH(1))
    f.instructions.append(ADD())       # x + 1
    f.instructions.append(CALL('g'))   # g(x + 1)
    f.instructions.append(LOAD(0))     # push x
    f.instructions.append(ADD())       # g(x+1) + x
    f.instructions.append(RET())       # return g(x+1) + x    
    # int g(int y) { return x + 2; }
    g = VMFrameTemplate('g', 1)
    g.instructions.append(STORE(0))    # y -> var[0]
    g.instructions.append(LOAD(0))     # push y
    g.instructions.append(PUSH(2))
    g.instructions.append(ADD())       # y + 2
    g.instructions.append(RET())       # return y + 2
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(10))
    main.instructions.append(CALL('f'))
    main.instructions.append(WRITE())
    vm = VM()
    vm.add_frame_template(f)
    vm.add_frame_template(g)
    vm.add_frame_template(main)
    vm.run()
    captured = capsys.readouterr()
    assert captured.out == '23'

#----------------------------------------------------------------------
# STRUCT RELATED
#----------------------------------------------------------------------

def test_create_two_no_field_struct(capsys):
    main = VMFrameTemplate('main', 0)
    main.instructions.append(ALLOCS())
    main.instructions.append(WRITE())
    main.instructions.append(ALLOCS())
    main.instructions.append(WRITE())    
    vm = VM()
    vm.add_frame_template(main)
    vm.run()
    captured = capsys.readouterr()
    assert captured.out == '20242025'

def test_create_single_one_field_struct(capsys):
    main = VMFrameTemplate('main', 0)
    main.instructions.append(ALLOCS())
    main.instructions.append(DUP())
    main.instructions.append(PUSH('blue'))
    main.instructions.append(SETF('field_1'))
    main.instructions.append(DUP())
    main.instructions.append(GETF('field_1'))
    main.instructions.append(WRITE())    
    vm = VM()
    vm.add_frame_template(main)
    vm.run()
    captured = capsys.readouterr()
    assert captured.out == 'blue'
    
def test_create_two_one_field_structs(capsys):
    main = VMFrameTemplate('main', 0)
    main.instructions.append(ALLOCS())
    main.instructions.append(STORE(0))           # x -> var[0]
    main.instructions.append(ALLOCS())
    main.instructions.append(STORE(1))           # y -> var[1]
    main.instructions.append(LOAD(0))
    main.instructions.append(PUSH('blue'))
    main.instructions.append(SETF('field_1'))    # x.field_1 = blue
    main.instructions.append(LOAD(1))
    main.instructions.append(PUSH('green'))
    main.instructions.append(SETF('field_1'))    # y.field_1 = green
    main.instructions.append(LOAD(0))
    main.instructions.append(GETF('field_1'))    # push x.field_1
    main.instructions.append(WRITE())
    main.instructions.append(LOAD(1))
    main.instructions.append(GETF('field_1'))    # push y.field_1
    main.instructions.append(WRITE())
    vm = VM()
    vm.add_frame_template(main)
    vm.run()
    captured = capsys.readouterr()
    assert captured.out == 'bluegreen'

def test_create_one_two_field_struct(capsys):
    main = VMFrameTemplate('main', 0)
    main.instructions.append(ALLOCS())
    main.instructions.append(STORE(0))           # x -> var[0]
    main.instructions.append(LOAD(0))
    main.instructions.append(PUSH('blue'))
    main.instructions.append(SETF('field_1'))    # x.field_1 = blue
    main.instructions.append(LOAD(0))
    main.instructions.append(PUSH('green'))
    main.instructions.append(SETF('field_2'))    # x.field_2 = green
    main.instructions.append(LOAD(0))
    main.instructions.append(GETF('field_1'))    # push x.field_1
    main.instructions.append(WRITE())
    main.instructions.append(LOAD(0))
    main.instructions.append(GETF('field_2'))    # push x.field_2
    main.instructions.append(WRITE())
    vm = VM()
    vm.add_frame_template(main)
    vm.run()
    captured = capsys.readouterr()
    assert captured.out == 'bluegreen'
    
def test_null_object_get_field():
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(None))
    main.instructions.append(GETF('field_1'))
    vm = VM()
    vm.add_frame_template(main)
    with pytest.raises(MyPLError) as e:
        vm.run()
    assert str(e.value).startswith('VM Error:')

def test_null_object_set_field():
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(None))
    main.instructions.append(PUSH('blue'))
    main.instructions.append(SETF('field_1'))
    vm = VM()
    vm.add_frame_template(main)
    with pytest.raises(MyPLError) as e:
        vm.run()
    assert str(e.value).startswith('VM Error:')

#----------------------------------------------------------------------
# ARRAY RELATED
#----------------------------------------------------------------------

def test_array_alloc(capsys):
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(10))  # array length
    main.instructions.append(ALLOCA())
    main.instructions.append(WRITE())
    main.instructions.append(PUSH(5))   # array length
    main.instructions.append(ALLOCA())
    main.instructions.append(WRITE())
    vm = VM()
    vm.add_frame_template(main)
    vm.run()
    captured = capsys.readouterr()
    assert captured.out == '20242025'

def test_bad_size_value_array_alloc():
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(-1))  # array length
    main.instructions.append(ALLOCA())
    vm = VM()
    vm.add_frame_template(main)
    with pytest.raises(MyPLError) as e:
        vm.run()
    assert str(e.value).startswith('VM Error:')

def test_bad_null_size_array_alloc():
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(None))  # array length
    main.instructions.append(ALLOCA())
    vm = VM()
    vm.add_frame_template(main)
    with pytest.raises(MyPLError) as e:
        vm.run()
    assert str(e.value).startswith('VM Error:')
    
def test_array_access(capsys):
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(5))    # array length
    main.instructions.append(ALLOCA())
    main.instructions.append(PUSH(0))    # index
    main.instructions.append(GETI())
    main.instructions.append(WRITE())
    vm = VM()
    vm.add_frame_template(main)
    vm.run()
    captured = capsys.readouterr()
    assert captured.out == 'null'

def test_bad_null_index_array_access():
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(10))  # array length
    main.instructions.append(ALLOCA())
    main.instructions.append(PUSH(None))
    main.instructions.append(GETI())
    vm = VM()
    vm.add_frame_template(main)
    with pytest.raises(MyPLError) as e:
        vm.run()
    assert str(e.value).startswith('VM Error:')

def test_bad_index_too_small_array_access():
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(10))  # array length
    main.instructions.append(ALLOCA())
    main.instructions.append(PUSH(-1))
    main.instructions.append(GETI())
    vm = VM()
    vm.add_frame_template(main)
    with pytest.raises(MyPLError) as e:
        vm.run()
    assert str(e.value).startswith('VM Error:')

def test_bad_index_too_large_array_access():
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(10))  # array length
    main.instructions.append(ALLOCA())
    main.instructions.append(PUSH(10))
    main.instructions.append(GETI())
    vm = VM()
    vm.add_frame_template(main)
    with pytest.raises(MyPLError) as e:
        vm.run()
    assert str(e.value).startswith('VM Error:')

def test_bad_null_array_access():
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(None))
    main.instructions.append(STORE(0))
    main.instructions.append(LOAD(0))
    main.instructions.append(PUSH(0)) # array index
    main.instructions.append(GETI())
    vm = VM()
    vm.add_frame_template(main)
    with pytest.raises(MyPLError) as e:
        vm.run()
    assert str(e.value).startswith('VM Error:')
    
def test_array_update(capsys):
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(5))      # array length
    main.instructions.append(ALLOCA())
    main.instructions.append(STORE(0))     # store oid
    main.instructions.append(LOAD(0))
    main.instructions.append(PUSH(0))      # index
    main.instructions.append(PUSH('blue')) # value
    main.instructions.append(SETI())
    main.instructions.append(LOAD(0))
    main.instructions.append(PUSH(0))      # index
    main.instructions.append(GETI())
    main.instructions.append(WRITE())
    vm = VM()
    vm.add_frame_template(main)
    vm.run()
    captured = capsys.readouterr()
    assert captured.out == 'blue'
    
def test_loop_with_index_updates(capsys):
    main = VMFrameTemplate('main', 0)
    # allocate 3-element array
    main.instructions.append(PUSH(3))      
    main.instructions.append(ALLOCA())
    main.instructions.append(STORE(0))
    # set index 0 to 2
    for i in range(3): 
        main.instructions.append(LOAD(0))       # oid
        main.instructions.append(PUSH(i))       # index
        main.instructions.append(PUSH(10 + i))  # value
        main.instructions.append(SETI())
    # get and print index 0 to 2
    for i in range(3):
        main.instructions.append(LOAD(0)) # oid
        main.instructions.append(PUSH(i)) # index
        main.instructions.append(GETI())
        main.instructions.append(WRITE())
    vm = VM()
    vm.add_frame_template(main)
    vm.run()
    captured = capsys.readouterr()
    assert captured.out == '101112'
    
def test_bad_null_array_update():
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(None))
    main.instructions.append(STORE(0))
    main.instructions.append(LOAD(0)) # oid
    main.instructions.append(PUSH(0)) # index
    main.instructions.append(PUSH(1)) # value
    main.instructions.append(SETI())
    vm = VM()
    vm.add_frame_template(main)
    with pytest.raises(MyPLError) as e:
        vm.run()
    assert str(e.value).startswith('VM Error:')

def test_bad_null_index_array_update():
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(10))
    main.instructions.append(ALLOCA())
    main.instructions.append(PUSH(None)) # index
    main.instructions.append(PUSH(1))    # value
    main.instructions.append(SETI())
    vm = VM()
    vm.add_frame_template(main)
    with pytest.raises(MyPLError) as e:
        vm.run()
    assert str(e.value).startswith('VM Error:')

def test_index_too_small_array_update():
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(10))
    main.instructions.append(ALLOCA())
    main.instructions.append(PUSH(-1)) # index
    main.instructions.append(PUSH(1))  # value
    main.instructions.append(SETI())
    vm = VM()
    vm.add_frame_template(main)
    with pytest.raises(MyPLError) as e:
        vm.run()
    assert str(e.value).startswith('VM Error:')

def test_index_too_large_array_update():
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(10))
    main.instructions.append(ALLOCA())
    main.instructions.append(PUSH(10)) # index
    main.instructions.append(PUSH(1))  # value
    main.instructions.append(SETI())
    vm = VM()
    vm.add_frame_template(main)
    with pytest.raises(MyPLError) as e:
        vm.run()
    assert str(e.value).startswith('VM Error:')

#----------------------------------------------------------------------
# BUILT-IN FUNCTIONS
#----------------------------------------------------------------------

def test_string_length(capsys):
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(''))
    main.instructions.append(LEN())
    main.instructions.append(WRITE())
    main.instructions.append(PUSH('blue'))
    main.instructions.append(LEN())
    main.instructions.append(WRITE())
    main.instructions.append(PUSH('green'))
    main.instructions.append(LEN())
    main.instructions.append(WRITE())
    vm = VM()
    vm.add_frame_template(main)
    vm.run()
    captured = capsys.readouterr()
    assert captured.out == '045'

def test_bad_null_string_length():
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(None))
    main.instructions.append(LEN())
    vm = VM()
    vm.add_frame_template(main)
    with pytest.raises(MyPLError) as e:
        vm.run()
    assert str(e.value).startswith('VM Error:')

def test_array_length(capsys):
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(0))
    main.instructions.append(ALLOCA())
    main.instructions.append(LEN())
    main.instructions.append(WRITE())
    main.instructions.append(PUSH(3))
    main.instructions.append(ALLOCA())
    main.instructions.append(LEN())
    main.instructions.append(WRITE())
    main.instructions.append(PUSH(10000))
    main.instructions.append(ALLOCA())
    main.instructions.append(LEN())
    main.instructions.append(WRITE())
    vm = VM()
    vm.add_frame_template(main)
    vm.run()
    captured = capsys.readouterr()
    assert captured.out == '0310000'
    
def test_bad_null_array_length():
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(None))
    main.instructions.append(LEN())
    vm = VM()
    vm.add_frame_template(main)
    with pytest.raises(MyPLError) as e:
        vm.run()
    assert str(e.value).startswith('VM Error:')
    
def test_get_characters_from_string(capsys):
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(0))
    main.instructions.append(PUSH('blue'))
    main.instructions.append(GETC())
    main.instructions.append(WRITE())
    main.instructions.append(PUSH(1))
    main.instructions.append(PUSH('blue'))
    main.instructions.append(GETC())
    main.instructions.append(WRITE())
    main.instructions.append(PUSH(2))
    main.instructions.append(PUSH('blue'))
    main.instructions.append(GETC())
    main.instructions.append(WRITE())
    main.instructions.append(PUSH(3))
    main.instructions.append(PUSH('blue'))
    main.instructions.append(GETC())
    main.instructions.append(WRITE())
    vm = VM()
    vm.add_frame_template(main)
    vm.run()
    captured = capsys.readouterr()
    assert captured.out == 'blue'

def test_bad_too_small_string_index():
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(-1))
    main.instructions.append(PUSH('blue'))
    main.instructions.append(GETC())
    vm = VM()
    vm.add_frame_template(main)
    with pytest.raises(MyPLError) as e:
        vm.run()
    assert str(e.value).startswith('VM Error:')

def test_bad_too_big_string_index():
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(4))
    main.instructions.append(PUSH('blue'))
    main.instructions.append(GETC())
    vm = VM()
    vm.add_frame_template(main)
    with pytest.raises(MyPLError) as e:
        vm.run()
    assert str(e.value).startswith('VM Error:')

def test_bad_null_string_index():
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(None))
    main.instructions.append(PUSH('blue'))
    main.instructions.append(GETC())
    vm = VM()
    vm.add_frame_template(main)
    with pytest.raises(MyPLError) as e:
        vm.run()
    assert str(e.value).startswith('VM Error:')

def test_bad_null_string_in_get():
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(0))
    main.instructions.append(PUSH(None))
    main.instructions.append(GETC())
    vm = VM()
    vm.add_frame_template(main)
    with pytest.raises(MyPLError) as e:
        vm.run()
    assert str(e.value).startswith('VM Error:')
    
def test_to_int(capsys):
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(3.14))
    main.instructions.append(TOINT())
    main.instructions.append(WRITE())
    main.instructions.append(PUSH('5'))
    main.instructions.append(TOINT())
    main.instructions.append(WRITE())
    vm = VM()
    vm.add_frame_template(main)
    vm.run()
    captured = capsys.readouterr()
    assert captured.out == '35'

def test_bad_string_to_int():
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH('bad int'))
    main.instructions.append(TOINT())
    vm = VM()
    vm.add_frame_template(main)
    with pytest.raises(MyPLError) as e:
        vm.run()
    assert str(e.value).startswith('VM Error:')

def test_bad_null_to_int():
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(None))
    main.instructions.append(TOINT())
    vm = VM()
    vm.add_frame_template(main)
    with pytest.raises(MyPLError) as e:
        vm.run()
    assert str(e.value).startswith('VM Error:')
    
def test_to_double(capsys):
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(3))
    main.instructions.append(TODBL())
    main.instructions.append(WRITE())
    main.instructions.append(PUSH('5.1'))
    main.instructions.append(TODBL())
    main.instructions.append(WRITE())
    main.instructions.append(PUSH('7'))
    main.instructions.append(TODBL())
    main.instructions.append(WRITE())    
    vm = VM()
    vm.add_frame_template(main)
    vm.run()
    captured = capsys.readouterr()
    assert captured.out == '3.05.17.0'
    
def test_bad_string_to_double():
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH('bad double'))
    main.instructions.append(TODBL())
    vm = VM()
    vm.add_frame_template(main)
    with pytest.raises(MyPLError) as e:
        vm.run()
    assert str(e.value).startswith('VM Error:')

def test_bad_null_to_double():
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(None))
    main.instructions.append(TODBL())
    vm = VM()
    vm.add_frame_template(main)
    with pytest.raises(MyPLError) as e:
        vm.run()
    assert str(e.value).startswith('VM Error:')

def test_to_string(capsys):
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(3))
    main.instructions.append(TOSTR())
    main.instructions.append(WRITE())
    main.instructions.append(PUSH(5.1))
    main.instructions.append(TOSTR())
    main.instructions.append(WRITE())
    main.instructions.append(PUSH('a string'))
    main.instructions.append(TOSTR())
    main.instructions.append(WRITE())    
    vm = VM()
    vm.add_frame_template(main)
    vm.run()
    captured = capsys.readouterr()
    assert captured.out == '35.1a string'

def test_bad_null_to_string():
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(None))
    main.instructions.append(TOSTR())
    vm = VM()
    vm.add_frame_template(main)
    with pytest.raises(MyPLError) as e:
        vm.run()
    assert str(e.value).startswith('VM Error:')


#----------------------------------------------------------------------
# CODE GENERATION TESTS
#----------------------------------------------------------------------

def test_empty_var_table():
    table = VarTable()
    assert len(table) == 0

def test_var_table_push_pop():
    table = VarTable()
    assert len(table) == 0
    table.push_environment()
    assert len(table) == 1
    table.pop_environment()
    assert len(table) == 0
    table.push_environment()
    table.push_environment()    
    assert len(table) == 2
    table.pop_environment()
    assert len(table) == 1
    table.pop_environment()
    assert len(table) == 0

def test_simple_var_table_add():
    table = VarTable()
    table.add('x')
    assert table.get('x') == None
    table.push_environment()
    table.add('x')
    assert table.get('x') == 0
    table.pop_environment()

def test_var_table_multiple_add():
    table = VarTable()
    table.push_environment()
    table.add('x')
    table.add('y')
    assert table.get('x') == 0
    assert table.get('y') == 1

def test_var_table_multiple_environments():
    table = VarTable()
    table.push_environment()
    table.add('x')
    table.add('y')
    table.push_environment()
    table.add('x')
    table.add('z')
    table.push_environment()
    table.add('u')
    assert table.get('x') == 2
    assert table.get('y') == 1
    assert table.get('z') == 3
    assert table.get('u') == 4
    table.pop_environment()
    assert table.get('x') == 2
    assert table.get('y') == 1
    assert table.get('z') == 3
    assert table.get('u') == None
    table.pop_environment()
    assert table.get('x') == 0
    assert table.get('y') == 1
    assert table.get('z') == None
    assert table.get('u') == None
    table.pop_environment()
    assert table.get('x') == None
    assert table.get('y') == None
    assert table.get('z') == None
    assert table.get('u') == None

    
#----------------------------------------------------------------------
# SIMPLE GETTING STARTED TESTS
#----------------------------------------------------------------------

# helper function to build and return a vm from the program string
def build(program):
    in_stream = FileWrapper(io.StringIO(program))
    vm = VM()
    cg = CodeGenerator(vm)
    ASTParser(Lexer(FileWrapper(io.StringIO(program)))).parse().accept(cg)
    return vm


def test_empty_program(capsys):
    program = 'void main() {}'
    build(program).run()
    captured = capsys.readouterr()
    assert captured.out == ''

def test_simple_print(capsys):
    program = 'void main() {print("blue");}'
    build(program).run()
    captured = capsys.readouterr()
    assert captured.out == 'blue'
    
#----------------------------------------------------------------------
# BASIC VARIABLES AND ASSIGNMENT
#----------------------------------------------------------------------

def test_simple_var_decls(capsys):
    program = (
        'void main() { \n'
        '  int x1 = 3; \n'
        '  double x2 = 2.7; \n'
        '  bool x3 = true; \n'
        '  string x4 = "abc"; \n'
        '  print(x1); \n'
        '  print(x2); \n'
        '  print(x3); \n'
        '  print(x4); \n'
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    assert captured.out == '32.7trueabc'

def test_simple_var_decl_no_expr(capsys):
    program = (
        'void main() { \n'
        '  int x; \n'
        '  print(x); \n'
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    assert captured.out == 'null'

def test_simple_var_assignments(capsys):
    program = (
        'void main() { \n'
        '  int x = 3; \n'
        '  print(x); \n'
        '  x = 4; \n'
        '  print(x); \n'
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    assert captured.out == '34'

#----------------------------------------------------------------------
# ARITHMETIC EXPRESSIONS
#----------------------------------------------------------------------

def test_simple_add(capsys):
    program = (
        'void main() { \n'
        '  int x = 4 + 5; \n'
        '  double y = 3.25 + 4.5; \n'
        '  string z = "ab" + "cd"; \n'
        '  print(x); \n'
        '  print(" "); \n'
        '  print(y); \n'
        '  print(" "); \n'        
        '  print(z); \n'
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    assert captured.out == '9 7.75 abcd'

def test_simple_sub(capsys):
    program = (
        'void main() { \n'
        '  int x = 6 - 5; \n'
        '  double y = 4.5 - 3.25; \n'
        '  print(x); \n'
        '  print(" "); \n'
        '  print(y); \n'
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    assert captured.out == '1 1.25'

def test_simple_mult(capsys):
    program = (
        'void main() { \n'
        '  int x = 4 * 3; \n'
        '  double y = 4.5 * 3.25; \n'
        '  print(x); \n'
        '  print(" "); \n'
        '  print(y); \n'
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    assert captured.out == '12 14.625'
    
def test_simple_div(capsys):
    program = (
        'void main() { \n'
        '  int x = 9 / 2; \n'
        '  double y = 4.5 / 1.25; \n'
        '  print(x); \n'
        '  print(" "); \n'
        '  print(y); \n'
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    assert captured.out == '4 3.6'

def test_longer_arithmetic_expr(capsys):
    program = (
        'void main() { \n'
        '  int x = 3 + (6 - 5) + (5 * 2) + (2 / 2); \n'
        '  print(x); \n'
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    assert captured.out == '15'
    
#----------------------------------------------------------------------
# BOOLEAN EXPRESSIONS
#----------------------------------------------------------------------

def test_simple_and(capsys):
    program = (
        'void main() { \n'
        '  bool x1 = true and true; \n'
        '  bool x2 = true and false; \n'
        '  bool x3 = false and true; \n'        
        '  bool x4 = false and false; \n'        
        '  print(x1); \n'
        '  print(" "); \n'
        '  print(x2); \n'
        '  print(" "); \n'
        '  print(x3); \n'
        '  print(" "); \n'
        '  print(x4); \n'
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    assert captured.out == 'true false false false'

def test_simple_or(capsys):
    program = (
        'void main() { \n'
        '  bool x1 = true or true; \n'
        '  bool x2 = true or false; \n'
        '  bool x3 = false or true; \n'        
        '  bool x4 = false or false; \n'        
        '  print(x1); \n'
        '  print(" "); \n'
        '  print(x2); \n'
        '  print(" "); \n'
        '  print(x3); \n'
        '  print(" "); \n'
        '  print(x4); \n'
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    assert captured.out == 'true true true false'

def test_simple_not(capsys):
    program = (
        'void main() { \n'
        '  bool x1 = not true; \n'
        '  bool x2 = not false; \n'
        '  print(x1); \n'
        '  print(" "); \n'
        '  print(x2); \n'
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    assert captured.out == 'false true'

def test_more_involved_logical_expression(capsys):
    program = (
        'void main() { \n'
        '  bool x = true or (true and false) or (false or (true and true)); \n'
        '  bool y = not ((not false) and (false or (true or false)) and true); \n'
        '  print(x); \n'
        '  print(" "); \n'
        '  print(y); \n'
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    assert captured.out == 'true false'
    

#----------------------------------------------------------------------
# COMPARISON OPERATORS
#----------------------------------------------------------------------

def test_true_numerical_comparisons(capsys):
    program = (
        'void main() { \n'
        '  bool x1 = 3 < 4; \n'
        '  bool x2 = 3 <= 4; \n'
        '  bool x3 = 3 <= 3; \n'
        '  bool x4 = 4 > 3; \n'
        '  bool x5 = 4 >= 3; \n'
        '  bool x6 = 3 >= 3; \n'
        '  bool x7 = 3 == 3; \n'
        '  bool x8 = 3 != 4; \n'
        '  print(x1 and x2 and x3 and x4 and x5 and x6 and x7 and x8); \n'
        '  bool y1 = 3.25 < 4.5; \n'
        '  bool y2 = 3.25 <= 4.5; \n'
        '  bool y3 = 3.25 <= 3.25; \n'
        '  bool y4 = 4.5 > 3.25; \n'
        '  bool y5 = 4.5 >= 3.25; \n'
        '  bool y6 = 3.25 >= 3.25; \n'
        '  bool y7 = 3.25 == 3.25; \n'
        '  bool y8 = 3.25 != 4.5; \n'
        '  print(y1 and y2 and y3 and y4 and y5 and y6 and y7 and y8); \n'
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    assert captured.out == 'truetrue'

def test_false_numerical_comparisons(capsys):
    program = (
        'void main() { \n'
        '  bool x1 = 4 < 3; \n'
        '  bool x2 = 4 <= 3; \n'
        '  bool x3 = 3 > 4; \n'
        '  bool x4 = 3 >= 4; \n'
        '  bool x5 = 3 == 4; \n'
        '  bool x6 = 3 != 3; \n'
        '  print(x1 or x2 or x3 or x4 or x5 or x6); \n'
        '  bool y1 = 4.5 < 3.25; \n'
        '  bool y2 = 4.5 <= 3.25; \n'
        '  bool y3 = 3.25 > 4.5; \n'
        '  bool y4 = 3.25 >= 4.5; \n'
        '  bool y5 = 3.25 == 4.5; \n'
        '  bool y6 = 3.25 != 3.25; \n'
        '  print(y1 or y2 or y3 or y4 or y5 or y6); \n'
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    assert captured.out == 'falsefalse'

def test_true_alphabetic_comparisons(capsys):
    program = (
        'void main() { \n'
        '  bool x1 = "a" < "b"; \n'
        '  bool x2 = "a" <= "b"; \n'
        '  bool x3 = "a" <= "a"; \n'
        '  bool x4 = "b" > "a"; \n'
        '  bool x5 = "b" >= "a"; \n'
        '  bool x6 = "a" >= "a"; \n'
        '  bool x7 = "a" == "a"; \n'
        '  bool x8 = "a" != "b"; \n'
        '  print(x1 and x2 and x3 and x4 and x5 and x6 and x7 and x8); \n'
        '  bool y1 = "aa" < "ab"; \n'
        '  bool y2 = "aa" <= "ab"; \n'
        '  bool y3 = "aa" <= "aa"; \n'
        '  bool y4 = "ab" > "aa"; \n'
        '  bool y5 = "ab" >= "aa"; \n'
        '  bool y6 = "aa" >= "aa"; \n'
        '  bool y7 = "aa" == "aa"; \n'
        '  bool y8 = "aa" != "ab"; \n'
        '  print(y1 and y2 and y3 and y4 and y5 and y6 and y7 and y8); \n'
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    assert captured.out == 'truetrue'
  
def test_false_alphabetic_comparisons(capsys):
    program = (
        'void main() { \n'
        '  bool x1 = "b" < "a"; \n'
        '  bool x2 = "b" <= "a"; \n'
        '  bool x3 = "a" > "b"; \n'
        '  bool x4 = "a" >= "b"; \n'
        '  bool x5 = "a" == "b"; \n'
        '  bool x6 = "a" != "a"; \n'
        '  print(x1 or x2 or x3 or x4 or x5 or x6); \n'
        '  bool y1 = "ab" < "aa"; \n'
        '  bool y2 = "ab" <= "aa"; \n'
        '  bool y3 = "aa" > "ab"; \n'
        '  bool y4 = "aa" >= "ab"; \n'
        '  bool y5 = "aa" == "ab"; \n'
        '  bool y6 = "aa" != "aa"; \n'
        '  print(y1 or y2 or y3 or y4 or y5 or y6); \n'
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    assert captured.out == 'falsefalse'
  
def test_null_comparisons(capsys):
    program = (
        'void main() { \n'
        '  int a = 3; \n'
        '  double b = 2.75; \n'
        '  string c = "abc"; \n'
        '  bool d = false; \n'
        '  print(null != null); \n'
        '  print((a == null) or (b == null) or (c == null) or (d == null)); \n'
        '  print((null == a) or (null == b) or (null == c) or (null == d)); \n'
        '  print(" "); \n'
        '  print(null == null); \n'
        '  print((a != null) and (b != null) and (c != null) and (d != null)); \n'
        '  print((null != a) and (null != b) and (null != c) and (null != d)); \n'
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    assert captured.out == 'falsefalsefalse truetruetrue'

    
#----------------------------------------------------------------------
# WHILE LOOPS
#----------------------------------------------------------------------

def test_basic_while(capsys):
    program = (
        'void main() { \n'
        '  int i = 0; \n'
        '  while (i < 5) { \n'
        '    i = i + 1;'
        '  } \n'
        '  print(i); \n'
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    assert captured.out == '5'
    
def test_more_involved_while(capsys):
    program = (
        'void main() { \n'
        '  int i = 0; \n'
        '  while (i < 7) { \n'
        '    int j = i * 2; \n'
        '    print(j); \n'
        '    print(" "); \n'
        '    i = i + 1;'
        '  } \n'
        '  print(i); \n'
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    assert captured.out == '0 2 4 6 8 10 12 7'

def test_nested_while(capsys):
    program = (
        'void main() { \n'
        '  int i = 0; \n'
        '  while (i < 5) { \n'
        '    print(i); \n'
        '    print(" "); \n'
        '    int j = 0; \n'
        '    while (j < i) { \n'
        '      print(j); \n'
        '      print(" "); \n'
        '      j = j + 1; \n'
        '    } \n'
        '    i = i + 1;'
        '  } \n'
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    print(captured.out)
    assert captured.out == '0 1 0 2 0 1 3 0 1 2 4 0 1 2 3 '

#----------------------------------------------------------------------
# FOR LOOPS
#----------------------------------------------------------------------

def test_basic_for(capsys):
    program = (
        'void main() { \n'
        '  for (int i = 0; i < 5; i = i + 1) { \n'
        '    print(i); \n'
        '    print(" "); \n'
        '  } \n'
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    print(captured.out)
    assert captured.out == '0 1 2 3 4 '

def test_nested_for(capsys):
    program = (
        'void main() { \n'
        '  int x = 0; \n'
        '  for (int i = 1; i <= 5; i = i + 1) { \n'
        '    for (int j = 1; j <= 4; j = j + 1) { \n'
        '      x = x + (i * j); \n'
        '    } \n'
        '  } \n'
        '  print(x); \n'
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    print(captured.out)
    assert captured.out == '150'

def test_for_outer_non_bad_shadowing(capsys):
    program = (
        'void main() { \n'
        '  int i = 32; \n'
        '  for (int i = 0; i < 5; i = i + 1) { \n'
        '    print(i); \n'
        '    print(" "); \n'
        '  } \n'
        '  print(i); \n'
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    print(captured.out)
    assert captured.out == '0 1 2 3 4 32'

#----------------------------------------------------------------------
# IF STATEMENTS
#----------------------------------------------------------------------

def test_just_an_if(capsys):
    program = (
        'void main() { \n'
        '  print("-"); \n'
        '  if (true) { \n'
        '    print(1); \n'
        '  } \n'
        '  print("-"); \n'
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    print(captured.out)
    assert captured.out == '-1-'
    
def test_consecutive_ifs(capsys):
    program = (
        'void main() { \n'
        '  print("-"); \n'
        '  if (3 < 4) { \n'
        '    print(1); \n'
        '  } \n'
        '  if (true) { \n'
        '    print(2); \n'
        '  } \n'
        '  if (3 > 4) { \n'
        '    print(3); \n'
        '  } \n'
        '  print("-"); \n'
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    print(captured.out)
    assert captured.out == '-12-'

def test_simple_else_ifs(capsys):
    program = (
        'void main() { \n'
        '  print("-"); \n'
        '  if (3 < 4) { \n'
        '    print(1); \n'
        '  } \n'
        '  elseif (4 > 3) { \n'
        '    print(2); \n'
        '  } \n'
        '  else { \n'
        '    print(3); \n'
        '  } \n'
        '  if (4 < 3) { \n'
        '    print(1); \n'
        '  } \n'
        '  elseif (3 < 4) { \n'
        '    print(2); \n'
        '  } \n'
        '  else { \n'
        '    print(3); \n'
        '  } \n'
        '  if (4 < 3) { \n'
        '    print(1); \n'
        '  } \n'
        '  elseif (3 != 3) { \n'
        '    print(2); \n'
        '  } \n'
        '  else { \n'
        '    print(3); \n'
        '  } \n'
        '  print("-"); \n'        
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    print(captured.out)
    assert captured.out == '-123-'

def test_many_else_ifs(capsys):
    program = (
        'void main() { \n'
        '  print("-"); \n'
        '  if (false) { \n'
        '    print(1); \n'
        '  } \n'
        '  elseif (false) { \n'
        '    print(2); \n'
        '  } \n'
        '  elseif (true) { \n'
        '    print(3); \n'
        '  } \n'
        '  elseif (true) { \n'
        '    print(4); \n'
        '  } \n'
        '  else { \n'
        '    print(5); \n'
        '  } \n'
        '  print("-"); \n'        
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    print(captured.out)
    assert captured.out == '-3-'
    

#----------------------------------------------------------------------
# FUNCTION CALLS
#----------------------------------------------------------------------

def test_no_arg_call(capsys):
    program = (
        'void f() {} \n'
        'void main() { \n'
        '  print(f()); \n'
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    print(captured.out)
    assert captured.out == 'null'

def test_one_arg_call(capsys):
    program = (
        'int f(int x) {return x;} \n'
        'void main() { \n'
        '  print(f(3)); \n'
        '  print(f(4)); \n'        
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    print(captured.out)
    assert captured.out == '34'
    
def test_two_arg_call(capsys):
    program = (
        'int f(int x, int y) {return x * y;} \n'
        'void main() { \n'
        '  print(f(3, 2)); \n'
        '  print(f(5, 6)); \n'        
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    print(captured.out)
    assert captured.out == '630'

def test_three_arg_call(capsys):
    program = (
        'int f(int x, int y, int z) {return (x * y) - z;} \n'
        'void main() { \n'
        '  print(f(3, 2, 4)); \n'
        '  print(f(5, 6, 10)); \n'        
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    print(captured.out)
    assert captured.out == '220'

def test_multi_level_call(capsys):
    program = (
        'string f(string s) {return s + "!";} \n'
        'string g(string s1, string s2) {return f(s1 + s2);} \n'
        'string h(string s1, string s2, string s3) {return g(s1, s2) + f(s3);} \n'
        'void main() { \n'
        '  print(h("red", "blue", "green")); \n'
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    print(captured.out)
    assert captured.out == 'redblue!green!'

def test_basic_recursion(capsys):
    program = (
        'int non_negative_sum(int x) { \n'
        '  if (x <= 0) {return 0;} \n'
        '  return x + non_negative_sum(x-1); \n'
        '} \n'

        'void main() { \n'
        '  print(non_negative_sum(0)); \n'
        '  print(" "); \n'
        '  print(non_negative_sum(1)); \n'
        '  print(" "); \n'
        '  print(non_negative_sum(10)); \n'
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    print(captured.out)
    assert captured.out == '0 1 55'

def test_fib_recursion(capsys):
    program = (
        'int fib(int n) { \n'
        '  if (n < 0) {return null;} \n'
        '  if (n == 0) {return 0;} \n'
        '  if (n == 1) {return 1;} \n'
        '  return fib(n-1) + fib(n-2); \n'
        '}\n'
        'void main() { \n'
        '  print(fib(8)); \n'
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    print(captured.out)
    assert captured.out == '21'

#----------------------------------------------------------------------
# STRUCTS
#----------------------------------------------------------------------

def test_empty_struct(capsys):
    program = (
        'struct T {} \n'
        'void main() { \n'
        '  T t = new T(); \n'
        '  print(t); \n'
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    print(captured.out)
    assert captured.out == '2024'

def test_simple_one_field_struct(capsys):
    program = (
        'struct T {int x;} \n'
        'void main() { \n'
        '  T t = new T(3); \n'
        '  print(t.x); \n'
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    print(captured.out)
    assert captured.out == '3'

def test_simple_two_field_struct(capsys):
    program = (
        'struct T {int x; bool y;} \n'
        'void main() { \n'
        '  T t = new T(3, true); \n'
        '  print(t.x); \n'
        '  print(" "); \n'
        '  print(t.y); \n'
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    print(captured.out)
    assert captured.out == '3 true'

def test_simple_assign_field(capsys):
    program = (
        'struct T {int x; bool y;} \n'
        'void main() { \n'
        '  T t = new T(3, true); \n'
        '  t.x = t.x + 1; \n'
        '  t.y = not t.y; \n'
        '  print(t.x); \n'
        '  print(" "); \n'
        '  print(t.y); \n'
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    print(captured.out)
    assert captured.out == '4 false'

def test_simple_struct_assign(capsys):
    program = (
        'struct T {int x; bool y;} \n'
        'void main() { \n'
        '  T t1 = new T(3, true); \n'
        '  T t2 = t1; \n'
        '  T t3; \n'
        '  t3 = t2; \n'
        '  t1.x = t1.x + 1; \n'
        '  print(t1.x); \n'
        '  print(" "); \n'
        '  print(t1.y); \n'
        '  print(" "); \n'
        '  print(t2.x); \n'
        '  print(" "); \n'
        '  print(t2.y); \n'
        '  print(" "); \n'        
        '  print(t3.x); \n'
        '  print(" "); \n'
        '  print(t3.y); \n'
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    print(captured.out)
    assert captured.out == '4 true 4 true 4 true'

def test_simple_two_structs(capsys):
    program = (
        'struct T1 {int val; T2 t2;} \n'
        'struct T2 {int val; T1 t1;} \n'
        'void main() { \n'
        '  T1 x = new T1(3, null); \n'
        '  T2 y = new T2(4, x); \n'
        '  x.t2 = y; \n'
        '  print(x.val); \n'
        '  print(" "); \n'
        '  print(x.t2.val); \n'
        '  print(" "); \n'
        '  print(y.val); \n'
        '  print(" "); \n'
        '  print(y.t1.val); \n'
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    print(captured.out)
    assert captured.out == '3 4 4 3'
    
def test_recursive_struct(capsys):
    program = (
        'struct Node {int val; Node next;} \n'
        'void main() { \n'
        '  Node r = new Node(10, null); \n'
        '  r.next = new Node(20, null); \n'
        '  r.next.next = new Node(30, null); \n'
        '  print(r); \n'
        '  print(" "); \n'
        '  print(r.val); \n'
        '  print(" "); \n'
        '  print(r.next); \n'
        '  print(" "); \n'
        '  print(r.next.val); \n'
        '  print(" "); \n'        
        '  print(r.next.next); \n'
        '  print(" "); \n'        
        '  print(r.next.next.val); \n'
        '  print(" "); \n'        
        '  print(r.next.next.next); \n'
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    print(captured.out)
    assert captured.out == '2024 10 2025 20 2026 30 null'

def test_struct_as_fun_param(capsys):
    program = (
        'struct Node {int val; Node next;} \n'
        'int val(Node n) {print(n); print(" "); return n.val;} \n'
        'void main() { \n'
        '  Node r = new Node(24, null); \n'
        '  print(val(r)); \n'
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    print(captured.out)
    assert captured.out == '2024 24'

#----------------------------------------------------------------------
# ARRAYS
#----------------------------------------------------------------------

def test_simple_array_creation(capsys):
    program = (
        'void main() { \n'
        '  array int xs = new int[5]; \n'
        '  print(xs); \n'
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    print(captured.out)
    assert captured.out == '2024'

def test_simple_array_access(capsys):
    program = (
        'void main() { \n'
        '  array int xs = new int[2]; \n'
        '  print(xs[0]); \n'
        '  print(" "); \n'
        '  print(xs[1]); \n'
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    print(captured.out)
    assert captured.out == 'null null'

def test_array_init(capsys):
    program = (
        'void main() { \n'
        '  array bool xs = new bool[3]; \n'
        '  xs[0] = false; \n'
        '  xs[1] = true; \n'
        '  print(xs[0]); \n'
        '  print(" "); \n'
        '  print(xs[1]); \n'
        '  print(" "); \n'
        '  print(xs[2]); \n'        
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    print(captured.out)
    assert captured.out == 'false true null'

def test_array_of_struct(capsys):
    program = (
        'struct T {bool x; int y;} \n'
        'void main() { \n'
        '  array T xs = new T[3]; \n'
        '  xs[0] = new T(true, 24); \n'
        '  xs[1] = new T(false, 48); \n'
        '  print(xs); \n'
        '  print(" "); \n'
        '  print(xs[0]); \n'
        '  print(" "); \n'        
        '  print(xs[0].x); \n'
        '  print(" "); \n'        
        '  print(xs[0].y); \n'
        '  print(" "); \n'        
        '  print(xs[1]); \n'
        '  print(" "); \n'        
        '  print(xs[1].x); \n'
        '  print(" "); \n'        
        '  print(xs[1].y); \n'
        '  print(" "); \n'        
        '  print(xs[2]); \n'
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    print(captured.out)
    assert captured.out == '2024 2025 true 24 2026 false 48 null'

def test_update_array_of_struct(capsys):
    program = (
        'struct T {bool x; int y;} \n'
        'void main() { \n'
        '  array T xs = new T[2]; \n'
        '  xs[0] = new T(true, 24); \n'
        '  xs[1] = new T(false, 48); \n'
        '  xs[0].x = not xs[0].x; \n'
        '  xs[0].y = xs[0].y + 1; \n'
        '  xs[1].x = not xs[1].x; \n'
        '  xs[1].y = xs[1].y + 1; \n'
        '  print(xs[0].y); \n'
        '  print(" "); \n'        
        '  print(xs[0].x); \n'
        '  print(" "); \n'        
        '  print(xs[1].y); \n'
        '  print(" "); \n'        
        '  print(xs[1].x); \n'
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    print(captured.out)
    assert captured.out == '25 false 49 true'

def test_update_path_ending_in_array(capsys):
    program = (
        'struct Node {int val; array Node next;} \n'
        'void main() { \n'
        '  Node n = new Node(20, new Node[2]); \n'
        '  n.next[0] = new Node(10, new Node[1]); \n'
        '  n.next[1] = new Node(30, null); \n'
        '  n.next[0].next[0] = new Node(5, null); \n'
        '  print(n.val); \n'
        '  print(" "); \n'        
        '  print(n.next[0].val); \n'
        '  print(" "); \n'        
        '  print(n.next[1].val); \n'
        '  print(" "); \n'        
        '  print(n.next[0].next[0].val); \n'
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    print(captured.out)
    assert captured.out == '20 10 30 5'

def test_array_as_param(capsys):
    program = (
        'bool val(array bools xs, int index) { \n'
        '  print(xs); \n'
        '  print(" "); \n'
        '  return xs[index]; \n'
        '} \n'
        'void main() { \n'
        '  array bool xs = new bool[5]; \n'
        '  xs[0] = true; \n'
        '  print(val(xs, 0)); \n'
        '  print(" "); \n'
        '  xs[1] = false; \n'
        '  print(val(xs, 1)); \n'
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    print(captured.out)
    assert captured.out == '2024 true 2024 false'
    
    
#----------------------------------------------------------------------
# BUILT-IN FUNCTIONS
#----------------------------------------------------------------------

def test_simple_to_str(capsys):
    program = (
        'void main() { \n'
        '  print(itos(24)); \n'
        '  print(" "); \n'
        '  print(dtos(3.14)); \n'
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    print(captured.out)
    assert captured.out == '24 3.14'

def test_simple_to_int(capsys):
    program = (
        'void main() { \n'
        '  print(stoi("24")); \n'
        '  print(" "); \n'
        '  print(dtoi(3.14)); \n'
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    print(captured.out)
    assert captured.out == '24 3'
    
def test_simple_to_double(capsys):
    program = (
        'void main() { \n'
        '  print(stod("3.14")); \n'
        '  print(" "); \n'
        '  print(itod(3)); \n'
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    print(captured.out)
    assert captured.out == '3.14 3.0'

def test_string_length(capsys):
    program = (
        'void main() { \n'
        '  print(length("")); \n'
        '  print(" "); \n'
        '  print(length("abcdefg")); \n'
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    print(captured.out)
    assert captured.out == '0 7'

def test_array_length(capsys):
    program = (
        'void main() { \n'
        '  print(length(new int[0])); \n'
        '  print(" "); \n'
        '  print(length(new int[7])); \n'
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    print(captured.out)
    assert captured.out == '0 7'
    
def test_string_get(capsys):
    program = (
        'void main() { \n'
        '  string s = "bluegreen"; \n'
        '  for (int i = 0; i < length(s); i = i + 1) { \n'
        '    print(get(i, s)); \n'
        '    print(" "); \n'
        '  } \n'
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    print(captured.out)
    assert captured.out == 'b l u e g r e e n '
    