def solve_matrix(A):
    "Solve a system of equations using gauss-jordan elimination."
    n = len(A)

    for i in range(0, n):
        max_cell = abs(A[i][i])
        max_row = i
        for k in range(i+1, n):
            if abs(A[k][i]) > max_cell:
                max_cell = abs(A[k][i])
                max_row = k

        for k in range(i, n+1):
            tmp = A[max_row][k]
            A[max_row][k] = A[i][k]
            A[i][k] = tmp

        for k in range(i+1, n):
            c = -A[k][i]/A[i][i]
            for j in range(i, n+1):
                if i == j:
                    A[k][j] = 0
                else:
                    A[k][j] += c * A[i][j]

    # Solve given the upper triangular matrix
    x = [0 for i in range(n)]
    for i in range(n-1, -1, -1):
        x[i] = A[i][n]/A[i][i]
        for k in range(i-1, -1, -1):
            A[k][n] -= A[k][i] * x[i]

    return x
