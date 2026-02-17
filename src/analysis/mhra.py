
import math

# MHRA = Medicines and Healthcare products Regulatory Agency

# | ------------- |   irAE   |
# | ------------- | yes | no |
# | ICI -   | yes | a   | b  |
# | Treated | no  | c   | d  |

def calcMHRAPRR(a, b, c, d):
    return a * (a + b + c + d) / (a + c) / (a + b)

def calcChiSquared(a, b, c, d):
    if any([x == 0 for x in [(a + b), (a + c), (c + d), (b + d)]]):
        return '0 value not valid'
    N = a + b + c + d
    return (((abs((a * d) - (b * c)) - (N / 2))**2) * N) / ((a + b) * (a + c) * (c + d) * (b + d))