import random


def prime_test(N, k):
	return fermat(N,k), miller_rabin(N,k)


def mod_exp(x, y, N):                       # y/2 recursive calls, or O(n) times.
    if y == 0:                              # Check all n bits in y, O(n) time.
        return 1                            # Return constant, so constant time.
    z = mod_exp(x, y//2, N)                 # y//2 is O(n) time to bit shift.
    if y % 2 == 0:                          # Checks last bit, so constant time.
        return ((z**2) % N)                 # z**2 is O(n^2), and % N is O(n^3),
    else:                                   # so O(n^3 + n^2), or O(n^3) time.
        return ((x * (z**2)) % N)           # O(n^2 + n^2 + n^3) = O(n^3) time.
	

def fprobability(k):  
    return 1 - 0.5**k                       # Both addition and exponentiation
                                            # (multiply n bits k times, or O(n^k)),
                                            # so O(n^k + n), or O(n^k) time.

def mprobability(k):
    # Composites will follow the pattern about 75% of the time, so there's a
    # 25% probability on each test for a false positive.
    return 1 - 0.25**k                      # O(n^k) time.


def fermat(N,k):
    for x in range(k):                      # k loops.
        a = random.randint(1, N-1)          # O(log (N-1)) time.
        if mod_exp(a, N-1, N) != 1:         # O(n^4) to run mod_exp.
            return 'composite'              # Constant time.
    return 'prime'                          # Constant time.


def miller_rabin(N,k):
    for x in range(k):                      # k loops
        a = random.randint(1, N-1)          # O(log (N-1))
        next_exp = N - 1                    # Subtraction, so O(n).

        # If the exponent starts out odd, then N is even and can't be prime.
        if next_exp % 2 == 1:               # Check last bit, constant time.
            return 'composite'              # Constant time.
        
        # Keep dividing by two on exponent as long as exponent is even.
        while next_exp % 2 == 0:            # At most runs n times, n = # of bits.
            step = mod_exp(a, next_exp, N)  # O(n^4) to run mod_exp
            if step == N-1:                 # Check each bit, O(n)
                return 'prime'              # Constant time.
            elif step != 1:                 # Check each bit, O(n)
                return 'composite'          # Constant time.
            next_exp //= 2                  # Bit shift, so O(n^2)

    # If every step resulted in one, assume the number is prime.
    return 'prime'                          # Constant time.
