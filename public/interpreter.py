import re

with open('sample.clean', 'r') as file:
    text = file.read()

class Token:
    def __init__(self, type, value):
        self.type = type
        self.value = value
    
class Tokenizer:
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.tokens = []
        self.indent_stack = [0]  # Maintain a stack for indentation levels
        self.indent_size = 4  # Assuming an indent size of 4 spaces

        self.token_types = {
            'OUT': r'\s*out:',
            'IN': r'\s*in:',
            'EQUAL_TO': r'\s*==',
            'NOT_EQUAL': r'\s*!=',
            'IDENTIFIER': r'\s*[a-zA-Z_][a-zA-Z0-9_]*',
            'ASSIGN': r'\s*=',
            'STRING': r'\s*\"([^"]*)\"',
            'NUMBER': r'\s*\d+',
            'GREATER_EQUAL': r'\s*>=',
            'LESS_EQUAL': r'\s*<=',
            'LESS_THAN': r'\s*<',
            'GREATER_THAN': r'\s*>',
            'SUBTRACTION': r'\s*-',
            'ADDITION': r'\s*\+',
            'LEFT_BRACKET': r'\s*\[',
            'RIGHT_BRACKET': r'\s*\]',
            'LEFT_BRACE': r'\s*\{',
            'RIGHT_BRACE': r'\s*\}',
            'PIPE': r'\|',
            'NEWLINE': r'\s*\n',
            'INDENT': None,
            'DEDENT': None
        }  


    def tokenize(self):

        lines = self.text.split('\n')

        for line in lines:

            if self.tokens and self.tokens[-1].type != 'INDENT' and self.tokens[-1].type != 'DEDENT':
                self.tokens.append(Token('NEWLINE', None))

            indent_level = self.get_indent_level(line)              # Check and handle indentation

            if indent_level > self.indent_stack[-1]:                
                self.tokens.append(Token('INDENT', None))           # Indent increased
                self.indent_stack.append(indent_level)

            elif indent_level < self.indent_stack[-1]:                
                while indent_level < self.indent_stack[-1]:         # Indent decreased
                    self.tokens.append(Token('DEDENT', None))
                    self.indent_stack.pop()
            
            tokens = self.tokenize_line_content(line)               # Tokenize line content
            self.tokens.extend(tokens)
        
        while len(self.indent_stack) > 1:                           # Add DEDENT tokens for remaining indentation levels
            self.tokens.append(Token('DEDENT', None))
            self.indent_stack.pop()
        return self.tokens

    def get_indent_level(self, line):
        return len(line) - len(line.lstrip())

    def tokenize_line_content(self, line):
        
        tokens = []
        pos = 0
        while pos < len(line):                                      # Iterate through token types and try to match each one
            matched = False
            for token_type, pattern in self.token_types.items():
                if pattern is not None:
                    regex = re.compile(pattern)
                    match = regex.match(line, pos)
                    if match:
                        value = match.group().strip()
                        tokens.append(Token(token_type, value))
                        pos = match.end()
                        matched = True
                        break
            
            if not matched:                                         # If no token type matched, raise an exception or handle invalid input
                raise Exception('Invalid syntax: %s' % line)
        return tokens

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current_token_index = 0
        self.indent_count = 0

    def match(self, token_type):
 
        if self.current_token_index < len(self.tokens):
            return self.tokens[self.current_token_index].type == token_type
        else:
            return False                            # If current token index exceeds the number of tokens, return False


    def parse(self):
        statements = []
        while self.current_token_index < len(self.tokens):
            # print(self.indent_count)
            statement = self.parse_statement()
            if statement:
                statements.append(statement)
        return statements


    def parse_statement(self):



        current_token = self.tokens[self.current_token_index]

        if current_token.type == 'IDENTIFIER':
            try:
                if self.tokens[self.current_token_index + 1].type == 'ASSIGN':
                    identifier = current_token

                    self.advance()                                              # Move to the ASSIGN token
                    self.advance()                                              # Move to the value token

                    value = self.parse_expression()                             # changed from value = self.tokens[self.current_token_index]

                    self.advance()                                              # Move to the next token

                    return {'type': 'Assignment', 'identifier': identifier.value, 'value': value}
            except Exception as e:
                print("Error: Solo identifier -> " + current_token.value)
                self.advance()
                return


        
        elif current_token.type == 'LEFT_BRACKET':

            return self.parse_conditional_block()
        
        elif current_token.type == 'LEFT_BRACE':
            
            return self.parse_if_conditional_block()

            
        elif current_token.type == 'OUT':

            self.advance()                              # move onto nextline which sould be newline
            self.advance()                              # skip over newline to next token

            print_block = self.parse_output()

            return {'type': 'Output', 'block': print_block}
        
        elif current_token.type == 'INDENT':
            self.indent_count += 1
            self.advance()
            return None

        elif current_token.type == 'DEDENT':
            self.indent_count -= 1
            self.advance()
            return None

        elif current_token.type == 'NEWLINE':
            self.advance()  
            return None
        

        else:
            raise Exception('Invalid syntax')

    def advance(self):
        self.current_token_index += 1

    def parse_output(self):
        
        print_block = []
        curr_count = 0

        if self.tokens[self.current_token_index].type == 'INDENT':
            self.indent_count += 1
            self.advance()
 
        if self.indent_count != 0:
            curr_count = self.indent_count

        while self.current_token_index < len(self.tokens) and self.indent_count >= curr_count:
            if self.tokens[self.current_token_index].type == 'DEDENT':
                self.indent_count -= 1
            elif (self.tokens[self.current_token_index].type != 'INDENT') and (self.tokens[self.current_token_index].type != 'NEWLINE'):
                print_block.append(self.tokens[self.current_token_index].value)
            self.advance()

        return print_block

    def parse_conditional_block(self):

        self.advance()                                      # move past the '['

        condition = self.parse_expression()

        if not self.match('RIGHT_BRACKET'):
            raise Exception('Expected RIGHT_BRACKET')
        self.advance()
        
        block = self.parse_block()                          # Parse the block of statements

        return {'type': 'ConditionalBlock', 'condition': condition, 'block': block}


    def parse_if_conditional_block(self):

        self.advance()                                      # move past the '['

        condition = self.parse_expression()

        if not self.match('RIGHT_BRACE'):
            raise Exception('Expected RIGHT_BRACE')
        self.advance()                                      # Move on from RIGHT_BRACE
        self.advance()                                      # Skip newline

        block = self.parse_block()                          # Parse the block of statements

        return {'type': 'IfConditionalBlock', 'condition': condition, 'block': block}


    def parse_expression(self):
        expression = []  # Initialize an empty list to store expressions
        while self.current_token_index < len(self.tokens):
            current_token = self.tokens[self.current_token_index]

            if current_token.type == 'IDENTIFIER' or current_token.type == 'NUMBER':
                expression.append(current_token.value.strip())
                self.advance()  # Move to the next token

            elif current_token.type == 'LESS_THAN':
                self.advance()  # Move past the LESS_THAN token
                expression.append({'type': 'LessThan', 'left': None, 'right': self.parse_expression()})

            elif current_token.type == 'GREATER_THAN':
                self.advance()  # Move past the GREATER_THAN token
                expression.append({'type': 'GreaterThan', 'left': None, 'right': self.parse_expression()})

            elif current_token.type == 'EQUAL_TO':
                self.advance()  # Move past the GREATER_THAN token
                expression.append({'type': 'EqualTo', 'left': None, 'right': self.parse_expression()})

            elif current_token.type == 'NOT_EQUAL':
                self.advance()  # Move past the GREATER_THAN token
                expression.append({'type': 'NotEqual', 'left': None, 'right': self.parse_expression()})

            elif current_token.type == 'GREATER_EQUAL':
                self.advance()  # Move past the GREATER_THAN token
                expression.append({'type': 'Greater_Equal', 'left': None, 'right': self.parse_expression()})

            elif current_token.type == 'LESS_EQUAL':
                self.advance()  # Move past the GREATER_THAN token
                expression.append({'type': 'Less_Equal', 'left': None, 'right': self.parse_expression()})

            elif current_token.type == 'LEFT_BRACKET':
                self.advance()  # Move past the LEFT_BRACKET token
                expression.append(self.parse_expression())
                if not self.match('RIGHT_BRACKET'):
                    raise Exception('Expected RIGHT_BRACKET')
                self.advance()  # Move past the RIGHT_BRACKET token

            elif current_token.type == 'LEFT_BRACE':
                self.advance()  # Move past the LEFT_BRACKET token
                expression.append(self.parse_expression())
                if not self.match('RIGHT_BRACE'):
                    raise Exception('Expected RIGHT_BRACE')
                self.advance()  # Move past the RIGHT_BRACKET token

            elif current_token.type in ('SUBTRACTION', 'ADDITION'):
                operator = current_token.value.strip()
                self.advance()  # Move past the operator
                right = self.parse_expression()  # Parse the right-hand side of the expression
                expression.append({'type': 'BinaryOperation', 'operator': operator, 'left': None, 'right': right})
            
            elif current_token.type == 'DEDENT':
                self.advance()
                self.indent_count -= 1

            elif current_token.type == 'INDENT':
                self.advance()
                self.indent_count += 1

            else:               # newline, rigth bracket / brace
                break  # Stop parsing if we encounter any other token type
            
        return expression


        
    def parse_block(self):
        block = []
        curr_count = 0
        
        if self.tokens[self.current_token_index].type == 'INDENT':
            self.indent_count += 1
            self.advance()
 
        if self.indent_count != 0:
            curr_count = self.indent_count

        while self.current_token_index < len(self.tokens) and self.indent_count >= curr_count: # and self.tokens[self.current_token_index].type != 'DEDENT'
            statement = self.parse_statement()
            if statement:
                block.append(statement)
        return block
        
class Interpret:
    def __init__(self):
        self.state = {}

    def varmap(self, var):
        if var in self.state:
            return self.state[var]
        return "Error: variable not found."

    def interpret(self, parsed):
        for statement in parsed:
            #print(statement)
            match statement['type']:
                case 'Assignment':
                    self.execute_assignment(statement)
                case 'ConditionalBlock':
                    self.execute_conditional(statement)
                case 'IfConditionalBlock':
                    self.execute_if_conditional(statement)
                case 'Output':
                    self.output(statement)
                case 'BinaryOperation':
                    self.eval_expr(statement)

    def execute_assignment(self, statement):
        var = statement['identifier']
        if len(statement['value']) == 1:
            val = self.eval_expr(statement['value'])
            self.state[var] = val
        else:
            stmt = statement['value']
            val = self.eval_expr(stmt)
            self.state[var] = val

    def execute_conditional(self, statement):
        condition = self.eval_condition(statement['condition'])
        while condition:
            self.interpret(statement['block'])
            condition = self.eval_condition(statement['condition'])

    def execute_if_conditional(self, statement):
        condition = self.eval_condition(statement['condition'])
        if condition: 
            self.interpret(statement['block'])

    def output(self, statement):
        if len(statement['block']) == 1:
            output_value = self.eval_expr(statement['block'])
            print(self.varmap(output_value))
        else:
            for i in range(len(statement['block'])):
                output_value = self.eval_expr(statement['block'][i])
                print(self.varmap(output_value))

    def eval_expr(self, expr):
        if isinstance(expr, int):
            return expr
        elif isinstance(expr, str):
            return expr                                     # must make return varmap val tbh
        elif isinstance(expr, list):
            if len(expr) == 1:
                return expr[0]
            else:
                var = expr[0]
                stmt = expr[1]
                rhs = self.eval_expr(stmt['right'])
                if rhs.isalpha():
                    rhs = self.varmap(rhs)
                match stmt['operator']:
                    case '+':
                        val = self.varmap(var)
                        val = int(val) + int(rhs)
                        return val
                    case '-':
                        val = self.varmap(var)
                        val = int(val) - int(rhs)
                        return val
                    case '*':
                        val = self.varmap(var)
                        val = int(val) * int(rhs)
                        return val
                    case '/':
                        val = self.varmap(var)
                        val = int(val) / int(rhs)
                        return val

            

    def eval_condition(self, cond):
        lhs = self.varmap(cond[0])
        expr = cond[1]                  # jsut the way i parsed
        rhs = self.eval_expr(expr['right'])
        match expr['type']:
            case 'EqualTo':
                return int(lhs) == int(rhs)
            case 'NotEqual':
                return int(lhs) != int(rhs)
            case 'GreaterThan':
                return int(lhs) > int(rhs)
            case 'LessThan':
                return int(lhs) < int(rhs)
            case 'Greater_Equal':
                return int(lhs) >= int(rhs)
            case 'Less_Equal':
                return int(lhs) <= int(rhs)

tokenizer = Tokenizer(text)
tokens = tokenizer.tokenize()
#for token in tokens:
#    print(token.type, token.value)

parser = Parser(tokens)
parsed = parser.parse()
# print(parsed)

#for statement in parsed:
#    print(statement)

interpreter = Interpret()
interpreter.interpret(parsed)
