import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        
        #initiating the creater class by the helper class 'crossword', and then defining the dmoains
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        
        #Function that return 2D array representing a given assignment.
        
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
        
        #The purpose of this function is to print crossword assignment to the terminal.
        
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def create_image(self, assignment, filename):
        
        #The purpose of this function is to create image from the puzzle we solved
        
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
        #solving the probelm by enforcing node consistency then using ac3 algorithm, then using the bactrack technique
        
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
            if any(result):
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
        #continue and append that word to the used_words list
            if value in used_words:
                return False
            
            used_words.append(value)

            #check if the length of the word is the same as the variable length
            if key.length != len(value):
                return False
            
            #get all the neighbors of that variable (becuase neighbors are the possible variable that has conflict), then check if the
            #neighbor is in the assignment dict, then get the overlaping index of the two variables (if any) and then compare the value 
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
        return True                
                        

    def order_domain_values(self, var, assignment):
        
        
        
        #The purpose of this function, is to return the values for a variables in list but sorted by the number of value sthey rule out for
        #the other overlaping variables, by that, the first value in the list, should be the one that rules out the fewest values among
        #other neighbors
        
        #Initiating an empty dict, with each value in that var domain, with value 0
        values_counter = {}
        
        for value in self.domains[var]:
            values_counter[value] = 0
            
            
        #Iterating over all the values in that variable domain
        for value in self.domains[var]:
            
            #then, iterating over each variable that is considered a neighbor of that variable
            for variable in self.crossword.neighbors(var):
                
                #after that, we iterate over each value in each neighbor variable
                for other_value in self.domains[variable]:
                    
                    #if there is and overlap between these two variables (the main variable and the neighbor var), we check there is a
                    #conflict and the value (our main value) is effected by that neighbor value, we increase that value counter by one
                    if self.crossword.overlaps[(var, variable)]:
                        
                        i,j = self.crossword.overlaps[var,variable]
                        
                        if value[i] != other_value[j]:
                                                   
                            values_counter[value] +=1
                         
        #after finishing our main loop, we returnt sorted list for that variable values, using the values counter as key
        return sorted([value for value in values_counter], key=lambda value: values_counter[value])

    def select_unassigned_variable(self, assignment, start_value = 1):
        
        #The purpose of this function is choose a variable that is NOT choosen yet in our assignment, the variable should be the one
        #with the fewest words remaining in its values, if a tie exist, the variabel choosen must be the one with highest number of 
        #neigbors, if tie exist return any variable from the tied variabels
        
        #Initiating an empty list that will contain our result(s)
        result = []
        
        #Initiating an empty dict that will contain our prospect variabels
        prospect_variables = {}
        
        #Iterating over each variable in the domain of our problem, if the variable exists in our assignment, we ignore it, if doesn't
        #we append it to our prospet variabels dict
        for variable,value in self.domains.items():
            
            if variable in assignment:
                continue
            else:
                prospect_variables[variable] = value
                
        #Iterating over each variable in our prospect dict, and starting with a value equals = 1 (because 1 is the fewest number of words), 
        #if the len of that variable value (the same as the number of remaining words) is equal to our starting value, we append it to the 
        #list result(s)
        for key, value in prospect_variables.items():
            if len(value) == start_value:
                result.append(key)
        
        #if after that the len of that list is 0, it means no variable met our value, so we recrusivly call the function again but we will 
        #increase the number of words to 2
        if len(result) == 0:
            return self.select_unassigned_variable(assignment,(start_value+1))
        
        #if result(s) contains value:
        else:
            
            #if there is more than one value, it means a tie, so we move to the next standard wich is the number of neighbors
            if len(result) > 1:
                neighbors_counter = {}
                
                #iterating over each variable in our list, and puting the number of neighbors to that variabels in a dict
                for var in result:
                    neighbors_counter[var] = len(self.crossword.neighbors(var))
                
                #return the one with the max number of neighbors
                return max(neighbors_counter, key=neighbors_counter.get)
            
            #if the len of result is not bigger than one, then returning the only variable 
            else:
                return result[0]

    def backtrack(self, assignment):
        
        #The purpose of this function is take partial assignment as using backtrack search return full assignment if possible,
        #if no possible assignment, return None
        
        #firstly, we check if the assignment given is complete, if so, we return it
        if self.assignment_complete(assignment):
            return assignment
        
        #we choose an assigned variable to work with using the function 'select_unassigned_variable'
        var = self.select_unassigned_variable(assignment)
        
        #then we iterate over the values (words) of that variable, and we assign one of these values to the assignment
        for value in self.order_domain_values(var, assignment):
            assignment[var] = value
            
            #we check if that assignmet is consistent using the function 'consistent'
            if self.consistent(assignment):
                
                
                #then we call recrusivly the backtrack function on the new assignment
                result = self.backtrack(assignment)
                
                #we check if that call does return True, if so, it means that the assignment is complete, so we return it
                if result:
                    return result
            
            #we remove that variable after we worked with it
            assignment.pop(var)
        
        #if no assignment is possible, return None, it means no solution for this puzzle
        return None


def main():

    

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        


if __name__ == "__main__":
    main()
