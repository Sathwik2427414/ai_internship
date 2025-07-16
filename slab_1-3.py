import numpy as np

def get_matrix_input(prompt):
    while True:
        try:
            rows = int(input(f"Enter the number of rows for {prompt}: "))
            cols = int(input(f"Enter the number of columns for {prompt}: "))
            if rows <= 0 or cols <= 0:
                print("Dimensions must be positive integers. Please try again.")
                continue

            matrix = []
            print(f"Enter elements for {prompt} row by row (space-separated):")
            for i in range(rows):
                while True:
                    row_str = input(f"Row {i + 1}: ")
                    try:
                        row = list(map(float, row_str.split()))
                        if len(row) != cols:
                            print(f"Expected {cols} elements, but got {len(row)}. Please re-enter row {i+1}.")
                        else:
                            matrix.append(row)
                            break
                    except ValueError:
                        print("Invalid input. Please enter numbers separated by spaces.")
            return np.array(matrix)
        except ValueError:
            print("Invalid input for dimensions. Please enter integers.")

def display_matrix(matrix, name="Matrix"):
    print(f"\n--- {name} ---")
    print(matrix)
    print("-" * (len(str(matrix).splitlines()[0])))

def matrix_addition():
    print("\n--- Matrix Addition (A + B) ---")
    matrix_a = get_matrix_input("Matrix A")
    matrix_b = get_matrix_input("Matrix B")

    if matrix_a.shape != matrix_b.shape:
        print("\nError: Matrices must have the same dimensions for addition.")
        return

    result = matrix_a + matrix_b
    display_matrix(matrix_a, "Matrix A")
    display_matrix(matrix_b, "Matrix B")
    display_matrix(result, "Result (A + B)")

def matrix_subtraction():
    print("\n--- Matrix Subtraction (A - B) ---")
    matrix_a = get_matrix_input("Matrix A")
    matrix_b = get_matrix_input("Matrix B")

    if matrix_a.shape != matrix_b.shape:
        print("\nError: Matrices must have the same dimensions for subtraction.")
        return

    result = matrix_a - matrix_b
    display_matrix(matrix_a, "Matrix A")
    display_matrix(matrix_b, "Matrix B")
    display_matrix(result, "Result (A - B)")

def matrix_multiplication():
    print("\n--- Matrix Multiplication (A x B) ---")
    matrix_a = get_matrix_input("Matrix A")
    matrix_b = get_matrix_input("Matrix B")

    if matrix_a.shape[1] != matrix_b.shape[0]:
        print("\nError: Number of columns in Matrix A must equal number of rows in Matrix B for multiplication.")
        return

    result = np.dot(matrix_a, matrix_b)
    display_matrix(matrix_a, "Matrix A")
    display_matrix(matrix_b, "Matrix B")
    display_matrix(result, "Result (A x B)")

def matrix_transpose():
    print("\n--- Matrix Transpose ---")
    matrix = get_matrix_input("the matrix to transpose")
    result = matrix.T
    display_matrix(matrix, "Original Matrix")
    display_matrix(result, "Transposed Matrix")

def matrix_determinant():
    print("\n--- Matrix Determinant ---")
    matrix = get_matrix_input("the square matrix to calculate determinant for")

    if matrix.shape[0] != matrix.shape[1]:
        print("\nError: Determinant can only be calculated for square matrices.")
        return
    if matrix.shape[0] > 20: # Arbitrary limit to prevent very long computations for huge matrices
        print("\nWarning: Calculating determinant for very large matrices can be computationally expensive.")
        print("For matrices larger than 20x20, consider specialized libraries or methods if performance is critical.")

    try:
        result = np.linalg.det(matrix)
        display_matrix(matrix, "Original Matrix")
        print(f"\nDeterminant: {result:.4f}")
    except np.linalg.LinAlgError:
        print("\nError: Cannot calculate determinant for this matrix (possibly singular).")

def main():
    print("Welcome to the Matrix Operations Tool!")

    while True:
        print("\nSelect an operation:")
        print("1. Matrix Addition (A + B)")
        print("2. Matrix Subtraction (A - B)")
        print("3. Matrix Multiplication (A x B)")
        print("4. Matrix Transpose")
        print("5. Matrix Determinant")
        print("6. Exit")

        choice = input("Enter your choice (1-6): ")

        if choice == '1':
            matrix_addition()
        elif choice == '2':
            matrix_subtraction()
        elif choice == '3':
            matrix_multiplication()
        elif choice == '4':
            matrix_transpose()
        elif choice == '5':
            matrix_determinant()
        elif choice == '6':
            print("Exiting Matrix Operations Tool. Goodbye!")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 6.")
        input("\nPress Enter to continue...") # Pause for user to see output

if __name__ == "__main__":
    main()