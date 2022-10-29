import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        
        #the purpose of this function is to solve the unary constrain ( which is the length of word ) by iterating over variables
        #and comparing each word in the values with the length and keeping only the words that satisfy this constrain
        
        #iterate over the variables
        for var in self.crossword.variables:
            unary_constrain = var.length
            
            #then iterate over each word in the set of values
            for word in self.domains[var].copy(): #iterating over a copy so the set doesn't change while iterating
                if len(word) == unary_constrain:
                    continue
                else:
                    self.domains[var].remove(word)

    def revise(self, x, y):
        
        #The purpose of this function is to make variable `x` arc consistent with variable `y` by removing values from 
        #the domain of x for which there is no  possible corresponding value for y in the domain of why.
        
        #Intitlizing variable with False value and if any change happened it becomes True and then return it
        revised = False
        
        #Since the overlap is represented by tuple (a,b) and a is the square that the letter in x variable must be the same as b in y
        #variable
        x_square = self.crossword.overlaps[(x,y)][0]
        y_square = self.crossword.overlaps[(x,y)][1]
        
        #copy_of_domains = self.domains.copy()

        #Iterating over each word in the x domain and representing the the sqaure by a variable called letter, then comparing this letter
        #with each letter in y variable in y sqaure and if once are the same, it is enough to keep that word, else we remove it
        for word in self.domains[x].copy():
            letter = word[x_square]
            result = []
            
            for y_word in self.domains[y].copy():
                if y_word[y_square] == letter:
                    result.append(True)
                else:
                    result.append(False)
            if all(result):
                #If we once added True, it is enough to keep the word, so we continue
                continue

            else:
                #if we didn't add any True, it means we have to remove the word
                self.domains[x].remove(word)
                revised = True
        return revised

    def ac3(self, arcs=None):
        #The purpose of this function is to update domain of each variable such that each variable is arc consistent with others
        
        #If the arcs is none, then we start with a list of all variables that overlaps in our problem
        if arcs == None:
            
            #Initlize an empty list of arcs if given as None
            arcs = []
            
            #Iterate over all variables that have an overlap and append them to our list
            for key, value in self.crossword.overlaps.items():
                if value is None:
                    continue
                else:
                    arcs.append(key)
                    
        #start to iterate, and as long as the arcs list NOT empty, we continoue
        while len(arcs) != 0:
            
            #We start with the first two variables in our list
            x,y = arcs.pop(0)
            
            #Then we check if revision happend, if yes then we go to the next step
            if self.revise(x,y):
                
                #If the domain of the variable X became empty, then we return False, becuase in such a case no solution will be avaiable
                if self.domains[x] is None:
                    return False
                
                #Else, we iterate over each neighbor of x, and we add the pair of variables to our list that we want to make consistency,
                #if we reached the same other variable, we don't add it
                for var in self.crossword.neighbors(x):
                    if var == y:
                        continue
                    else:
                        arcs.append((var,x))
        
        #If everything went fine, we return True, it means that our ac3 algorithm, worked fine
        return True

    def assignment_complete(self, assignment):
        
        #The purpose of this function to check if assignment done for all variables
        
        #Iterate over all variables in our problem
        for variable in self.domains:
            
            #check that every variable is in the assignment dict, if one variable not there, return False
            if variable not in assignment:
                return False
        
        #If everything went fine, return True    
        return True

    def consistent(self, assignment):
        
        #The purpose of this function is to check 3 things:
        #1- That each word was assigned to a variable is unique
        #2- That each word was assigned to a variable has a length same as the variable was assigned to
        #3- That there is no conflict in the overlaping charecters 
        
        used_words = []
        
        #Iterate over each variable and word in the assignment dict
        for key, value in assignment.items():
            
        #if the value is in the used_words list, return False, else
        #continue and append that word to the used_words list'
            if value in used_words:
                return False
            
            used_words.append(value)

            #check if the length of the word as same as the variable length
            if key.length != len(value):
                return False
            
            #get all the neighbors of that variable (becuase neighbors are the possible variable that has conflict), the check if the
            # neighbor is in the assignment dict, then get the overlaping index of the two variables (if any) and then compare the value 
            #of that variable with the value of that neighbor at that index, if the same, return False
            neighbors = self.crossword.neighbors(key)
            
            #iterate over each neighbor
            for neighbor in neighbors:
                
                if neighbor in assignment:
                    other_value = assignment[neighbor]
                    if self.crossword.overlaps[key,neighbor]:
                        i, j = self.crossword.overlaps[key,neighbor]
                        if value[i] != other_value[j]:
                            return False

    def order_domain_values(self, var, assignment):
        
        raise NotImplementedError

    def select_unassigned_variable(self, assignment):
        
        raise NotImplementedError

    def backtrack(self, assignment):
        
        raise NotImplementedError


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
