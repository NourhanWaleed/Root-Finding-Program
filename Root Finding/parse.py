from sympy import *
from exceptions import *
import main
import json

#some rules when passing strings:
# e has to be capital E
# multiplication has to be x*y and not xy , same in 2*x not 2x etc...

#TODO: test more
#TODO: output to file

def get_expression(expression):
    x = Symbol('x')
    try:
        expression_parsed = sympify(expression,convert_xor=True)
    except :
        raise badExpression('Expression cannot be solved.')
    else:
        return x , expression_parsed

def call_bisection(lower_bound,upper_bound,expression,error_tolerance=0.00001,max_step=50,fileName='out/bisectionOut.json'):
    x , expression_parsed = get_expression(expression)
    f = lambda y:float( expression_parsed.subs(x,y))
    return main.bisection(lower_bound,upper_bound,error_tolerance,f,max_step,fileName)


def call_false_position(lower_bound,upper_bound,expression,error_tolerance=0.00001,max_step=50,fileName='out/falsePosOut.json'):
    x,expression_parsed = get_expression(expression)
    f = lambda y: float(expression_parsed.subs(x,y))
    return main.false_position(lower_bound,upper_bound,error_tolerance,f,max_step,fileName)

def call_newton_raphson(initial_guess,expression,error_tolerance=0.00001,max_step=50,fileName='out/newtonOut.json'):
    x ,  expression_parsed = get_expression(expression)
    f = lambda y : float(expression_parsed.subs(x,y))
    try:
        f_dash = diff(expression_parsed,x)
        g = lambda y : float(f_dash.subs(x,y))
    except:
        raise cannotDiffererntiate('Cannot find a differentaition for this expression.\n')
    
    return main.newton_raphson(initial_guess,error_tolerance,max_step,f,g,fileName)


def call_fixed_point(initial_guess,expression,error_tolerance=0.00001,max_step=50,fileName='out/fixedPointOut.json'):
    x, expression_parsed = get_expression(expression)
    g = lambda y: float(expression_parsed.subs(x,y))
    return(main.fixed_point_iteration(initial_guess,error_tolerance,max_step,g,fileName=fileName))

def call_secant(guess1,guess2,expression,error_tolerance=0.00001,max_step=50,fileName='out/secantOut.json'):
    x, expression_parsed = get_expression(expression)
    f = lambda y: float(expression_parsed.subs(x,y))
    return main.secant(guess2,guess1,error_tolerance,max_step,f,fileName=fileName)

def fileToDict(fileName = 'input.json'):
    f = open(fileName,'r')
    data = json.load(f)
    f.close()
    return data

def call_from_file(fileName='input.json'):
    try:
        return call_from_dict(fileToDict(fileName))
    except badDictionary:
        raise badFile("File %s is incompatible or corrupted or has missing arguments." %fileName)

def call_from_dict(data):
    try:
        method = data['method'].lower()
        if method == 'bisection':
            return call_bisection(
                lower_bound=data['lower bound'],
                upper_bound=data['upper bound'],
                expression=data['expression'],
                error_tolerance=data.get('error tolerance',0.00001),
                max_step=data.get('max step',50),
                fileName=data.get('file path','out/bisectionOut.json')
            )
        elif method == 'false position' or method == 'regula falsi':
            return call_false_position(
                lower_bound=data['lower bound'],
                upper_bound=data['upper bound'],
                expression=data['expression'],
                error_tolerance=data.get('error tolerance',0.00001),
                max_step=data.get('max step',50),
                fileName=data.get('file path','out/falsePosOut.json')
            )
        elif method == 'newton raphson':
            return call_newton_raphson(
                initial_guess=data['initial guess'],
                expression=data['expression'],
                error_tolerance=data.get('error tolerance',0.00001),
                max_step=data.get('max step',50),
                fileName=data.get('file path','out/newtonOut.json')            
            )
        elif method == 'fixed point' or method == 'regula falsi':
            return call_fixed_point(
                initial_guess=data['initial guess'],
                expression=data['expression'],
                error_tolerance=data.get('error tolerance',0.00001),
                max_step=data.get('max step',50) ,
                fileName=data.get('file path','out/fixedPointOut.json')
            )
        elif method == 'secant':
            return call_secant(
                guess1= data['first guess'],
                guess2=data['second guess'],
                expression=data['expression'],
                error_tolerance=data.get('error tolerance',0.00001),
                max_step=data.get('max step',50),
                fileName=data.get('file path','out/secantOut.json')    
            )
    except KeyError as e:
        print(e)
        raise badDictionary("Missing input data." )

          