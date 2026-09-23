from typing import Any
from queue import Queue


class CSP:
    def __init__(
        self,
        variables: list[str],
        domains: dict[str, set],
        edges: list[tuple[str, str]],
    ):
        """Constructs a CSP instance with the given variables, domains and edges.
        
        Parameters
        ----------
        variables : list[str]
            The variables for the CSP
        domains : dict[str, set]
            The domains of the variables
        edges : list[tuple[str, str]]
            Pairs of variables that must not be assigned the same value
        """
        self.variables = variables
        self.domains = domains

        # Binary constraints as a dictionary mapping variable pairs to a set of value pairs.
        #
        # To check if variable1=value1, variable2=value2 is in violation of a binary constraint:
        # if (
        #     (variable1, variable2) in self.binary_constraints and
        #     (value1, value2) not in self.binary_constraints[(variable1, variable2)]
        # ) or (
        #     (variable2, variable1) in self.binary_constraints and
        #     (value1, value2) not in self.binary_constraints[(variable2, variable1)]
        # ):
        #     Violates a binary constraint
        self.binary_constraints: dict[tuple[str, str], set] = {}
        for variable1, variable2 in edges:
            self.binary_constraints[(variable1, variable2)] = set()
            for value1 in self.domains[variable1]:
                for value2 in self.domains[variable2]:
                    if value1 != value2:
                        self.binary_constraints[(variable1, variable2)].add((value1, value2))
                        self.binary_constraints[(variable1, variable2)].add((value2, value1))

    def ac_3(self) -> bool:
        """Performs AC-3 on the CSP.
        Meant to be run prior to calling backtracking_search() to reduce the search for some problems.
        
        Returns
        -------
        bool
            False if a domain becomes empty, otherwise True
        """
        
        # Ready the que of arcs to work through.
        queue = Queue()
        for variable1, variable2 in self.binary_constraints.keys():
            # Add both orientations of the edge to the queue, since edges are only stored in one orientation.
            queue.put((variable1, variable2))
            queue.put((variable2, variable1))

        while not queue.empty():
            variable1, variable2 = queue.get()
            
            # Revise the domain of variable1 to satisfy the binary constraint with variable2.
            if self.revise(variable1, variable2):
                if len(self.domains[variable1]) == 0:
                    # If the domain of variable1 is empty, then the CSP is unsatisfiable.
                    return False
                for neighbor in self.get_neighbors(variable1):
                    # Add the arc (neighbor, variable1) to the queue for further processing.
                    if neighbor != variable2:
                        queue.put((neighbor, variable1))
        return True

    def backtracking_search(self) -> None | dict[str, Any]:
        """Performs backtracking search on the CSP.
        
        Returns
        -------
        None | dict[str, Any]
            A solution if any exists, otherwise None
        """
        # Counters for a single summary line at the end of the search
        calls = 0
        failures = 0

        def backtrack(assignment: dict[str, Any]) -> None | dict[str, Any]:
            nonlocal calls, failures
            calls += 1

            # Escape condition: if all variables are assigned, return the assignment
            if len(assignment) == len(self.variables):
                return assignment
            
            # Select an unassigned variable at random (first)
            unassigned = [v for v in self.variables if v not in assignment]
            variable = unassigned[0]
            
            # Loop through all values in the variable's domain
            for value in self.domains[variable]:
                # Check if the value is consistent with the assignment and the binary constraints:
                is_consistent = self.is_consistent(variable, value, assignment)
                if not is_consistent:
                    pass
                else:
                    # If the value is consistent, add it to the assignment and continue with the next variable
                    assignment[variable] = value
                    
                    # Recursively call backtrack() with the new assignment
                    result = backtrack(assignment)
                    
                    if result is not None:
                        # If the recursive call returns a solution, return it. Otherwise, continue with the next value.
                        return result
                    else:
                        # If the recursive call did not return a solution, remove the variable from the assignment and continue with the next value.
                        del assignment[variable]
            failures += 1
            return None

        result = backtrack({})
        print(f"backtrack() calls: {calls}, failures: {failures}")
        return result
    
    def is_consistent(self, variable, value, assignment) -> bool:
        """Checks whether the given value is consistent with the current assignment for the given variable.

        Parameters
        ----------
            variable : str
                The variable to check
            value : int
                The value to check
            assignment : dict[str, int]
                The current assignment

        Returns
        -------
        bool
            True if the value is consistent, False otherwise.
        """
        # Check against all other variables in the assignment.
        for other, other_value in assignment.items():
            # Check first if there is a binary constraint between the two variables, and then check if the value pair is allowed by the constraint.
            if ((variable, other) in self.binary_constraints and
                    (value, other_value) not in self.binary_constraints[(variable, other)]):
                return False
            # Check the other orientation of the edge, since edges are only stored in one orientation.
            if ((other, variable) in self.binary_constraints and
                    (value, other_value) not in self.binary_constraints[(other, variable)]):
                return False
        return True

    def revise(self, variable1: str, variable2: str) -> bool:
        """Revises the domain of variable1 to satisfy the binary constraint with variable2.
        
        Parameters
        ----------
        variable1 : str
            The first variable
        variable2 : str
            The second variable

        Returns
        -------
        bool
            True if the domain of variable1 was revised, otherwise False
        """
        # Edges are only stored in one orientation, so look the constraint up both ways.
        # The value pairs are symmetric, so (value1, value2) works against either key.
        allowed = self.binary_constraints.get((variable1, variable2))
        if allowed is None:
            allowed = self.binary_constraints.get((variable2, variable1))
        if allowed is None:
            # No constraint between these two variables, so there is nothing to prune
            return False

        revised = False
        for value1 in set(self.domains[variable1]):
            satisfies_constraint = any(
                (value1, value2) in allowed
                for value2 in self.domains[variable2]
            )
            if not satisfies_constraint:
                self.domains[variable1].remove(value1)
                revised = True
        return revised
    
    def get_neighbors(self, variable: str) -> list[str]:
        """Returns a list of variables that are neighbors of the given variable.
        
        Parameters
        ----------
        variable : str
            The variable to find neighbors for

        Returns
        -------
        list[str]
            List of neighboring variables
        """
        neighbors = set()
        for (var1, var2) in self.binary_constraints.keys():
            if var1 == variable:
                neighbors.add(var2)
            elif var2 == variable:
                neighbors.add(var1)
        return list(neighbors)

def alldiff(variables: list[str]) -> list[tuple[str, str]]:
    """Returns a list of edges interconnecting all of the input variables
    
    Parameters
    ----------
    variables : list[str]
        The variables that all must be different

    Returns
    -------
    list[tuple[str, str]]
        List of edges in the form (a, b)
    """
    return [(variables[i], variables[j]) for i in range(len(variables) - 1) for j in range(i + 1, len(variables))]
