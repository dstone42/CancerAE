
import math
import numpy as np

# https://bmjopen.bmj.com/content/bmjopen/13/1/e068127.full.pdf

# ROR = Reporting odds ratio

# | ------------- |   irAE   |
# | ------------- | yes | no |
# | ICI -   | yes | a   | b  |
# | Treated | no  | c   | d  |

def calcROR(a, b, c, d):
    if any([x == 0 for x in [b, c]]):
        return '0 value in denominator'
    return (a * d) / (b * c)

# RORCI = Reporting odds ratio confidence interval

def calcRORCI(ROR, a, b, c, d):
    
    if any([x == 0 for x in [a, b, c, d]]):
        return '0 value in denominator', '0 value in denominator'

    se = math.sqrt((1 / a) + (1 / b) + (1 / c) + (1 / d))

    lowerBound = math.e**(np.log(ROR) - 1.96 * se)
    upperBound = math.e**(np.log(ROR) + 1.96 * se)

    return lowerBound, upperBound