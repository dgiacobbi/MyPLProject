"""Unit testing made specifically for list
cases. These are created for the project, and it ensures
that the lists are properly being compiled at each step.
Some unit tests were influenced by S. Bowers unit tests 
for HW.

NAME: David Giacobbi
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


# helper function to build and return a vm from the program string
def build(program):
    in_stream = FileWrapper(io.StringIO(program))
    vm = VM()
    cg = CodeGenerator(vm)
    ASTParser(Lexer(FileWrapper(io.StringIO(program)))).parse().accept(cg)
    return vm


#----------------------------------------------------------------------
# LEXER TEST CASES (2 TESTS)
#----------------------------------------------------------------------
def test_list_reserved_words():
    in_stream = FileWrapper(io.StringIO('list append clear max min'))
    l = Lexer(in_stream)
    t = l.next_token()
    assert t.token_type == TokenType.LIST
    assert t.lexeme == 'list'
    assert t.line == 1
    assert t.column == 1
    t = l.next_token()
    assert t.token_type == TokenType.APPEND
    assert t.lexeme == 'append'
    assert t.line == 1
    assert t.column == 6
    t = l.next_token()
    assert t.token_type == TokenType.CLEAR
    assert t.lexeme == 'clear'
    assert t.line == 1
    assert t.column == 13
    t = l.next_token()
    assert t.token_type == TokenType.MAX
    assert t.token_type == TokenType.MAX
    assert t.lexeme == 'max'
    assert t.line == 1
    assert t.column == 19
    t = l.next_token()
    assert t.token_type == TokenType.MIN
    assert t.token_type == TokenType.MIN
    assert t.lexeme == 'min'
    assert t.line == 1
    assert t.column == 23

def test_invalid_case_list_words():
    in_stream = FileWrapper(io.StringIO('Append'))
    l = Lexer(in_stream)
    t = l.next_token()
    assert t.token_type != TokenType.APPEND
    assert t.token_type == TokenType.ID
    in_stream = FileWrapper(io.StringIO('List'))
    l = Lexer(in_stream)
    t = l.next_token()
    assert t.token_type != TokenType.LIST
    assert t.token_type == TokenType.ID
    in_stream = FileWrapper(io.StringIO('Clear'))
    l = Lexer(in_stream)
    t = l.next_token()
    assert t.token_type != TokenType.CLEAR
    assert t.token_type == TokenType.ID
    in_stream = FileWrapper(io.StringIO('Max'))
    l = Lexer(in_stream)
    t = l.next_token()
    assert t.token_type != TokenType.MAX
    assert t.token_type == TokenType.ID 
    in_stream = FileWrapper(io.StringIO('Min'))
    l = Lexer(in_stream)
    t = l.next_token()
    assert t.token_type != TokenType.MIN
    assert t.token_type == TokenType.ID 


#----------------------------------------------------------------------
# PARSER TEST CASES (8 TESTS)
#----------------------------------------------------------------------
def test_list_var_decl():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  list int x1; \n'
        '} \n'
    ))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs[0].stmts) == 1
    assert p.fun_defs[0].stmts[0].var_def.data_type.is_array == True
    assert p.fun_defs[0].stmts[0].var_def.data_type.is_list == True
    assert p.fun_defs[0].stmts[0].var_def.data_type.type_name.lexeme == 'int'
    assert p.fun_defs[0].stmts[0].var_def.var_name.lexeme == 'x1'


def test_list_append_stmt():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  x1.append(8); \n'
        '  x1.x2.x3.append(8);'
        '} \n'
    ))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs[0].stmts) == 2
    assert p.fun_defs[0].stmts[0].function.token_type == TokenType.APPEND
    assert len(p.fun_defs[0].stmts[0].list_path) == 1
    assert p.fun_defs[0].stmts[1].function.token_type == TokenType.APPEND
    assert len(p.fun_defs[0].stmts[1].list_path) == 3


def test_list_clear_stmt():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  x1.clear(); \n'
        '  x1.x2.x3.clear();'
        '} \n'
    ))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs[0].stmts) == 2
    assert p.fun_defs[0].stmts[0].function.token_type == TokenType.CLEAR
    assert len(p.fun_defs[0].stmts[0].list_path) == 1
    assert p.fun_defs[0].stmts[1].function.token_type == TokenType.CLEAR
    assert len(p.fun_defs[0].stmts[1].list_path) == 3


def test_list_pop_stmt():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  x1.pop(); \n'
        '  x1.x2.x3.pop();'
        '} \n'
    ))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs[0].stmts) == 2
    assert p.fun_defs[0].stmts[0].function.token_type == TokenType.POP
    assert len(p.fun_defs[0].stmts[0].list_path) == 1
    assert p.fun_defs[0].stmts[1].function.token_type == TokenType.POP
    assert len(p.fun_defs[0].stmts[1].list_path) == 3


def test_list_max():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  x = xs.max(); \n'
        '  for (int i = 0; i < 45; i = xs.ys.max()){} \n'
        '} \n'
    ))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs[0].stmts) == 2
    assert p.fun_defs[0].stmts[0].expr.first.rvalue.fun_name.token_type == TokenType.MAX
    assert len(p.fun_defs[0].stmts[0].expr.first.rvalue.list_path) == 1
    assert p.fun_defs[0].stmts[1].assign_stmt.expr.first.rvalue.fun_name.token_type == TokenType.MAX
    assert p.fun_defs[0].stmts[1].assign_stmt.expr.first.rvalue.list_path[0].var_name.lexeme == "xs"
    assert len(p.fun_defs[0].stmts[1].assign_stmt.expr.first.rvalue.list_path) == 2


def test_list_min():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  x = xs.y[3].x[2].min(); \n'
        '  for (int i = 0; i < 45; i = xs.ys[3].x.ls[4].min()){} \n'
        '} \n'
    ))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs[0].stmts) == 2
    assert p.fun_defs[0].stmts[0].expr.first.rvalue.fun_name.token_type == TokenType.MIN
    assert len(p.fun_defs[0].stmts[0].expr.first.rvalue.list_path) == 3
    assert p.fun_defs[0].stmts[1].assign_stmt.expr.first.rvalue.fun_name.token_type == TokenType.MIN
    assert p.fun_defs[0].stmts[1].assign_stmt.expr.first.rvalue.list_path[2].var_name.lexeme == "x"
    assert len(p.fun_defs[0].stmts[1].assign_stmt.expr.first.rvalue.list_path) == 4


def test_simple_list_assignment():
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


def test_multiple_list_path_assignment():
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
# SEMANTIC CHECKER TEST CASES
#----------------------------------------------------------------------

# List declarations
def test_simple_list_declarations_sem():
    in_stream = FileWrapper(io.StringIO(
        'void main() {'
        '   list int x; \n'
        '   list double y; \n'
        '   list string z; \n'
        '   list bool w;'
        '} \n'
    ))
    ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())

def test_simple_list_struct_declarations_sem():
    in_stream = FileWrapper(io.StringIO(
        'struct S1 {list double r;} \n'
        'void main() { \n'
        '   list double m; \n'
        '   S1 p1 = new S1(m); \n'
        '} \n'
    ))
    ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())

def test_bad_list_declarations_sem():
    in_stream = FileWrapper(io.StringIO(
        'struct S1 {list double r;} \n'
        'void main() {'
        '   list double x;'
        '   list bool w;'
        '   S1 p1 = new S1(x);'
        '   S1 p2 = new S1(w);'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')

# List assignments
def test_simple_list_assignments_sem():
    in_stream = FileWrapper(io.StringIO(
        'void main() {'
        '   list int x; \n'
        '   x[43] = 2;\n'
        '   list double y; \n'
        '   y[22] = 2.345; \n'
        '   list bool z; \n'
        '   z[18] = false; \n'
        '   list string yz; \n'
        '   yz[18] = "hello"; \n'
        '} \n'
    ))
    ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())

def test_bad_list_assignments_sem():
    in_stream = FileWrapper(io.StringIO(
        'void main() {'
        '   list int x; \n'
        '   x[43] = 2;\n'
        '   list double y; \n'
        '   y[22] = 2.345; \n'
        '   list bool z; \n'
        '   z[18] = 18.3; \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')

# List function statements
def test_simple_int_list_fun_stmt_sem():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '   list int x; \n'
        '   x.append(4); \n'
        '   x.clear(); \n'
        '   x.pop(); \n'
        '} \n'
    ))
    ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())

def test_simple_double_list_fun_stmt_sem():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '   list double x; \n'
        '   x.append(4.789); \n'
        '   x.clear(); \n'
        '   x.pop(); \n'
        '} \n'
    ))
    ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())

def test_simple_bool_list_fun_stmt_sem():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '   list bool x; \n'
        '   x.append(true); \n'
        '   x.clear(); \n'
        '   x.pop(); \n'
        '} \n'
    ))
    ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())

def test_simple_string_list_fun_stmt_sem():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '   list string x; \n'
        '   x.append("hello"); \n'
        '   x.clear(); \n'
        '   x.pop(); \n'
        '} \n'
    ))
    ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())

def test_bad_append_stmt_sem():
    in_stream = FileWrapper(io.StringIO(
        'struct S1 {list double r;} \n'
        'void main() {'
        '   list double x;'
        '   x.append(14);'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')

# List rvalue statements
def test_simple_list_rvalue_sem():
    in_stream = FileWrapper(io.StringIO(
        'void main() {'
        '   list int x; \n'
        '   int z = x.max(); \n'
        '   bool r = (z > x.min()); \n'
        '} \n'
    ))
    ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())

def test_bad_list_rvalue_sem():
    in_stream = FileWrapper(io.StringIO(
        'void main() {'
        '   list int x; \n'
        '   double z = x.max(); \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')

def test_bad_string_list_rvalue_sem():
    in_stream = FileWrapper(io.StringIO(
        'void main() {'
        '   list string x; \n'
        '   string z = x.max(); \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')


#----------------------------------------------------------------------
# VM OPCODE TEST CASES
#----------------------------------------------------------------------

# ALLOCL
def test_list_allocation_vm(capsys):
    main = VMFrameTemplate('main', 0)
    main.instructions.append(ALLOCL())
    main.instructions.append(LEN())
    main.instructions.append(WRITE())
    main.instructions.append
    vm = VM()
    vm.add_frame_template(main)
    vm.run()
    captured = capsys.readouterr()
    assert captured.out == '0'

# MAX
def test_list_max_vm(capsys):
    main = VMFrameTemplate('main', 0)
    main.instructions.append(ALLOCL())
    main.instructions.append(DUP())
    main.instructions.append(PUSH(10)) # index
    main.instructions.append(APP())  # value
    main.instructions.append(DUP())
    main.instructions.append(PUSH(5)) # index
    main.instructions.append(APP())  # value
    main.instructions.append(MAX())
    main.instructions.append(WRITE())
    vm = VM()
    vm.add_frame_template(main)
    vm.run()
    captured = capsys.readouterr()
    assert captured.out == '10'

def test_bad_list_max_vm(capsys):
    main = VMFrameTemplate('main', 0)
    main.instructions.append(ALLOCL())
    main.instructions.append(DUP())
    main.instructions.append(PUSH(10)) # index
    main.instructions.append(APP())  # value
    main.instructions.append(DUP())
    main.instructions.append(PUSH(5)) # index
    main.instructions.append(APP())  # value
    main.instructions.append(MAX())
    main.instructions.append(WRITE())
    vm = VM()
    vm.add_frame_template(main)
    vm.run()
    captured = capsys.readouterr()
    assert captured.out != '5'

# MIN
def test_list_min_vm(capsys):
    main = VMFrameTemplate('main', 0)
    main.instructions.append(ALLOCL())
    main.instructions.append(DUP())
    main.instructions.append(PUSH(7)) # index
    main.instructions.append(APP())  # value
    main.instructions.append(DUP())
    main.instructions.append(PUSH(13)) # index
    main.instructions.append(APP())  # value
    main.instructions.append(MIN())
    main.instructions.append(WRITE())
    vm = VM()
    vm.add_frame_template(main)
    vm.run()
    captured = capsys.readouterr()
    assert captured.out == '7'

def test_bad_list_min_vm(capsys):
    main = VMFrameTemplate('main', 0)
    main.instructions.append(ALLOCL())
    main.instructions.append(DUP())
    main.instructions.append(PUSH(7)) # index
    main.instructions.append(APP())  # value
    main.instructions.append(DUP())
    main.instructions.append(PUSH(13)) # index
    main.instructions.append(APP())  # value
    main.instructions.append(MIN())
    main.instructions.append(WRITE())
    vm = VM()
    vm.add_frame_template(main)
    vm.run()
    captured = capsys.readouterr()
    assert captured.out != '13'

# CLEAR
def test_list_clear_vm(capsys):
    main = VMFrameTemplate('main', 0)
    main.instructions.append(ALLOCL())
    main.instructions.append(DUP())
    main.instructions.append(PUSH(7)) # index
    main.instructions.append(APP())  # value
    main.instructions.append(DUP())
    main.instructions.append(PUSH(13)) # index
    main.instructions.append(APP())  # value
    main.instructions.append(DUP())
    main.instructions.append(CLEAR())
    main.instructions.append(LEN())
    main.instructions.append(WRITE())
    vm = VM()
    vm.add_frame_template(main)
    vm.run()
    captured = capsys.readouterr()
    assert captured.out == '0'

# POPL
def test_list_popl_vm(capsys):
    main = VMFrameTemplate('main', 0)
    main.instructions.append(ALLOCL())
    main.instructions.append(DUP())
    main.instructions.append(PUSH(7)) # index
    main.instructions.append(APP())  # value
    main.instructions.append(DUP())
    main.instructions.append(PUSH(13)) # index
    main.instructions.append(APP())  # value
    main.instructions.append(DUP())
    main.instructions.append(POPL())
    main.instructions.append(LEN())
    main.instructions.append(WRITE())
    vm = VM()
    vm.add_frame_template(main)
    vm.run()
    captured = capsys.readouterr()
    assert captured.out == '1'

# APP
def test_list_app_vm(capsys):
    main = VMFrameTemplate('main', 0)
    main.instructions.append(ALLOCL())
    main.instructions.append(DUP())
    main.instructions.append(PUSH(7)) # index
    main.instructions.append(APP())  # value
    main.instructions.append(DUP())
    main.instructions.append(PUSH(13)) # index
    main.instructions.append(APP())  # value
    main.instructions.append(DUP())
    main.instructions.append(PUSH(45)) # index
    main.instructions.append(APP())  # value
    main.instructions.append(LEN())
    main.instructions.append(WRITE())
    vm = VM()
    vm.add_frame_template(main)
    vm.run()
    captured = capsys.readouterr()
    assert captured.out == '3'


#----------------------------------------------------------------------
# CODE GENERATION TEST CASES
#----------------------------------------------------------------------

# List allocation
def test_list_allocation_code_gen(capsys):
    program = (
        'void main() { \n'
        '  list int x; \n'
        '  for (int i = 0; i < 10; i = i + 1){ \n'
        '      x.append(i); \n'
        '  }'
        '  print(x);'
        '  print(" ");'
        '  print(length(x));'
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    assert captured.out == '2024 10'

# List assignment
def test_list_assignment_code_gen(capsys):
    program = (
        'void main() { \n'
        '  list int x; \n'
        '  for (int i = 0; i < 10; i = i + 1){ \n'
        '      x.append(2*i); \n'
        '  }'
        '  print(x[3]);'
        '  print(" ");'
        '  print(x[5]);'
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    assert captured.out == '6 10'

# List functions
def test_list_append_code_gen(capsys):
    program = (
        'void main() { \n'
        '  list int x; \n'
        '  for (int i = 0; i < 10; i = i + 1){ \n'
        '      x.append(2); \n'
        '  }'
        '  list double y; \n'
        '  for (int i = 0; i < 10; i = i + 1){ \n'
        '      y.append(2.3456); \n'
        '  }'
        '  list string x; \n'
        '  for (int i = 0; i < 10; i = i + 1){ \n'
        '      x.append("a"); \n'
        '  }'
        '  list bool x; \n'
        '  for (int i = 0; i < 10; i = i + 1){ \n'
        '      x.append(true); \n'
        '  }'
        '} \n'
    )
    build(program).run()

def test_list_clear_code_gen(capsys):
    program = (
        'void main() { \n'
        '  list int x; \n'
        '  for (int i = 0; i < 10; i = i + 1){ \n'
        '      x.append(2); \n'
        '  } \n'
        '  x.clear(); \n'
        '  print(length(x));'
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    assert captured.out == '0'

def test_list_pop_code_gen(capsys):
    program = (
        'void main() { \n'
        '  list int x; \n'
        '  for (int i = 0; i < 10; i = i + 1){ \n'
        '      x.append(2); \n'
        '  } \n'
        '  x.pop() \n;'
        '  print(length(x)); \n'
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    assert captured.out == '9'

# List rvalues
def test_list_max_code_gen(capsys):
    program = (
        'void main() { \n'
        '  list int x; \n'
        '  for (int i = 0; i < 10; i = i + 1){ \n'
        '      x.append(2*i); \n'
        '  } \n'
        '  print(x.max()); \n'
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    assert captured.out == '18'

def test_list_min_code_gen(capsys):
    program = (
        'void main() { \n'
        '  list int x; \n'
        '  for (int i = 0; i < 10; i = i + 1){ \n'
        '      x.append(2*i); \n'
        '  } \n'
        '  print(x.min()); \n'
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    assert captured.out == '0'