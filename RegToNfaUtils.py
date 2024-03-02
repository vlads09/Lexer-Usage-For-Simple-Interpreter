def priority(char: chr) -> int:
    """
    This function finds the priority of an operator

    Args:
        char (chr): the operator

    Returns:
        the priority -> higher number equals lower priority
    """
    match char:
        case '*': return 1
        case '?': return 1
        case '+': return 1
        case '&': return 2
        case '|': return 3
        case _: return 4

def isoperation(char: chr) -> bool:
    operators = ['|', '*', '+', '?', '&']
    
    return char in operators

def issugar(cnt_sugar: int, sugar: bool) -> (int, bool):
    """
    Skips the syntactic sugar elements from being analysed
    in order to analyse the next element from the regex

    Args:
        cnt_sugar: counter for how many steps are left to skip 
        sugar: if analysation of the regex is still at the body of the
        syntactic sugar

    Returns:
        Updated arguments
    """
    cnt_sugar -= 1
    if not cnt_sugar:
        sugar = False
    return (cnt_sugar, sugar)

def verify_concat(concat: bool, new_regex: str, character: str) -> (bool, str):
    """
    This function adds the concatenation character to the regex.
    
    Args:
        concat: if the concatenation character can be added
        new_regex: building string of the regex with the concatenation character
        character: character to be added to the new_regex

    Returns:
        Updated values of the new_regex and concat
    """
    if concat:
        new_regex += '&' + character
    else:
        new_regex += character
        concat = True
    return (concat, new_regex)

def verify_concat_left_para(concat: bool, new_regex: str, character: str) -> (bool, str):
    """
    This function adds the concatenation character to the regex
    and it ends the concatenation process because of the '(' character 

    Args:
        concat: if the concatenation character can be added
        new_regex: building string of the regex with the concatenation character
        character: character to be added to the new_regex

    Returns:
        Updated values of the new_regex and concat
    """
    if concat:
        new_regex += '&' + character
        concat = False
    else:
        new_regex += character
    
    return (concat, new_regex)

def operator_preprocess(concat: bool, new_regex: str, character: str) -> (bool, str):
    """
    This function adds the operator to the new built up regex.
    
    Args:
        concat: if the concatenation character can be added
        new_regex: building string of the regex with the concatenation character
        character: character to be added to the new_regex

    Returns:
        Updated values of the new_regex and concat
    """
    # check if the concatenation process ends
    if character == '|':
        concat = False
    new_regex += character
    return (concat, new_regex)

def preprocess_regex(regex: str) -> str:
    """
    This function creates a new regex which has the concatenation character
    included so the Shunting Yard algorithm could be applied in process_regex
    function

    Args:
        regex: given regex as string

    Returns:
        The updated regex as string
    """
    concat = False
    sugar = False
    cnt_sugar = 0
    # variable that helps skip a step
    # since hitting backslash will analyse
    # the special character that has backslash
    was_backslash = False
    new_regex = ''
    for index, character in enumerate(regex):
        if was_backslash:
            was_backslash = False
            continue
        elif sugar:
            (cnt_sugar, sugar) = issugar(cnt_sugar, sugar)
            continue
        elif character == '(':
            (concat, new_regex) = verify_concat_left_para(concat, new_regex, character)
        elif character == ')':
            new_regex += character
            concat = True
        elif character == '\\':
            (concat, new_regex) = verify_concat(concat, new_regex, regex[index:index + 2])
            was_backslash = True
        elif character == '[':
            sugar = True
            cnt_sugar = 4
            (concat, new_regex) = verify_concat(concat, new_regex, regex[index:index + 5])
        elif not isoperation(character) and character != ' ':
            (concat, new_regex) = verify_concat(concat, new_regex, character)
        elif isoperation(character):
            (concat, new_regex) = operator_preprocess(concat, new_regex, character)
            
    return new_regex

def add_operations(stack: [], queue: []) -> ([], []):
    """
    When reaching a ')', add all the operations from
    the stack until reaching '(' character to the queue

    Args:
        stack: stack filled with operations
        queue: Shunting Yard queue where Thompson algorithm will be applied
    Returns:
        Updated stack and queue 
    """
    while stack:
        elem = stack.pop()
        if elem == '(':
            break
        queue.append(elem)
    return (stack, queue)

def add_operation_to_stack(stack:[], queue: [], character: str) -> ([], []):
    """
        Adds a new operation to the stack
    Args:
        stack: Shunting Yard stack
        queue: Shunting Yard queue
        character: the operation

    Returns:
        The stack and the queue updated
    """
    # if there exists an operator already on the top of the operator stack 
    # with lower or equal value returned from
    # the priority function, than current input symbol, remove the operator 
    # from the top of the operations stack and append it 
    # to the output queue. Do this until the current input symbol 
    # has lower or equal value returned from
    # the priority function than the symbol 
    # on the top of the operator stack, or the operator stack is empty.
    while stack:
        elem = stack.pop()
        if priority(elem) <= priority(character):
            queue.append(elem)
        else:
            stack.append(elem)
            break
    stack.append(character)
    return (stack, queue)

def process_regex(regex: str) -> list:
    """
    This function applies Shunting Yard algorithm on regex.
    
    Documentation: 
    https://blog.cernera.me/converting-regular-expressions-to-postfix-notation-with-the-shunting-yard-algorithm/

    Returns:
        Shunting Yard Queue on which Thompson algorithm will be applied
    """
    stack = []
    queue = []
    sugar = False
    cnt_sugar = 0
    # variable that helps skip a step
    # since hitting backslash will analyse
    # the special character that has backslash
    was_backslash = False
    new_regex = preprocess_regex(regex)
    for index, character in enumerate(new_regex):
        if was_backslash:
            was_backslash = False
            continue
        elif sugar:
            (cnt_sugar, sugar) = issugar(cnt_sugar, sugar)
            continue
        if character == '\\':
            # special symbols case
            queue.append(new_regex[index:index + 2])
            was_backslash = True
        elif character == '[':
            # syntactic sugar case
            sugar = True
            cnt_sugar = 4
            queue.append(new_regex[index:index + 5])
        elif character == '(':
            stack.append('(')
        elif character == ')':
            (stack, queue) = add_operations(stack, queue)
        elif not isoperation(character):
            # if symbol, append it directly to the output queue
            queue.append(character)
        elif isoperation(character):
            (stack, queue) = add_operation_to_stack(stack, queue, character)
    queue.extend([stack.pop() for _ in range(len(stack))])
    return queue
