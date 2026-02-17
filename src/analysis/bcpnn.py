
import math

# https://bmjopen.bmj.com/content/bmjopen/13/1/e068127.full.pdf

class BCPNN:

    # | ------------- |   irAE   |
    # | ------------- | yes | no |
    # | ICI -   | yes | a   | b  |
    # | Treated | no  | c   | d  |

    def __init__(self, a, b, c, d) -> None:
        
        self.a = a
        self.b = b
        self.c = c
        self.d = d
        self.N = self.a + self.b + self.c + self.d

        # HYPER PARAMETERS

        self.gammaIJ = 1
        self.alphaI = 1
        self.betaJ = 1
        self.alpha = 2
        self.beta = 2
        self.cIJ = a
        self.cI = a + b
        self.cJ = a + c
        
        self.gamma = (self.gammaIJ * ((self.N + self.alpha) * (self.N + self.beta))) / ((self.cI + self.alphaI) * (self.cJ + self.betaJ))

        # Calculated

        self.E = None
        self.V = None
        

    # IC = Information Component

    def calcIC(self):
        if any([x == 0 for x in [(self.a * self.N), (self.a + self.c), (self.a + self.b)]]):
            return '0 value not valid'
        return math.log2((self.a * self.N) / ((self.a + self.c) * (self.a + self.b)))
    
    # Exp or E(IC) = Expected Function

    def calcExp(self):
        return math.log2(((self.cIJ + self.gammaIJ) * self.gamma) / (self.N + self.gamma))
    
    # Var or V(IC) = Variance Function

    def calcVar(self):
        return ((self.N - self.cIJ + self.gamma - self.gammaIJ) / (((self.cIJ + self.gammaIJ) * (1 + self.N + self.gamma)) + ((self.N - self.cI + self.alpha - self.alphaI) / ((self.cI + self.alphaI) * (1 + self.N + self.alpha)) + ((self.N - self.cJ + self.beta - self.betaJ) / ((self.cI + self.betaJ) * (1 + self.N + self.beta)))))) / math.log10(2)**2


    # ICCI = Information Component Confidence Interval

    def calcICCI(self):
        if self.E == None:
            self.E = self.calcExp()
        if self.V == None:
            self.V = self.calcVar()
        
        lowerBound = self.E - (2 * math.sqrt(self.V))
        upperBound = self.E + (2 * math.sqrt(self.V))

        return lowerBound, upperBound
    


def main():

    nn = BCPNN(10, 30, 5, 100)
    print(nn.calcIC())
    print(nn.calcICCI())



if __name__ == '__main__':
    main()