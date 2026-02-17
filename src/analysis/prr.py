
import math
import numpy as np

# https://bmjopen.bmj.com/content/bmjopen/13/1/e068127.full.pdf

# PRR = Proportional Reporting Ratio

# | ------------- |   irAE   |
# | ------------- | yes | no |
# | ICI -   | yes | a   | b  |
# | Treated | no  | c   | d  |

def calcPRR(a, b, c, d):
    if any([x == 0 for x in [a + b, c + d]]):
        return '0 value in denominator'
    elif (c / (c + d)) == 0:
        return '0 value in denominator'
    return (a / (a + b)) / (c / (c + d))

# PRRCI = Proportional Reporting Ratio Confidence Interval

def calcPRRCI(PRR, a, b, c, d):

    if any([x == 0 for x in [a, b, c, d]]):
        return '0 value in denominator', '0 value in denominator'
    
    se = math.sqrt((1 / a) + (1 / b) + (1 / c) + (1 / d))

    lowerBound = math.e**(np.log(PRR) - 1.96 * se)
    upperBound = math.e**(np.log(PRR) + 1.96 * se)

    return lowerBound, upperBound


