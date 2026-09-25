import numpy as np

#cipher alphabets
default = "abcdefghijklmnopqrstuvwxyz"
vowels = "aeiou"
consonants = "bcdfghjklmnpqrstvwxyz"
qwerty = "qwertyuiopasdfghjklzxcvbnm"
ambidextrous = "ambidextrous"

#messages used to demonstrate the encoding and decoding
bond = "Agent 007: \"Shaken, not stirred!\""
holmes = "[At 221B Baker Street] Holmes (to Watson): \"Elementary, my dear Watson!\""
joker = "Why so serious?! Let's put a smile on that face."
turing = "In 1950, Turing asked: \"Can machines think?\""
hamlet = "[Act 3, Scene 1] To be, or not to be?"
enigma = "[Bletchley, 1941] The Enigma has been cracked!"

messages = [bond, holmes, joker, turing, hamlet, enigma]


def gcd(a, b):
    #compute gcd using Euclid's algorithm
    while b:
        a, b = b, a % b
    return a


#created a base cipher that other ciphers inherit
class base_cipher:
    def _apply_maps(self, encode_map, decode_map, alphabet):
        #apply an encode or decode map to a particular character char
        apply_map = lambda char, map: (
        map.get(char.lower()).upper() if char.isupper() 
        else map.get(char.lower())
        ) if char.lower() in alphabet else char

        self.encode_char = lambda char: apply_map(char, encode_map)
        self.decode_char = lambda char: apply_map(char, decode_map)
    
    #encoding and decoding functions - error checking for messages that aren't of type string
    def encode(self, text):
        if not isinstance(text, str):
            raise Exception("message must be of type string")
        return "".join(map(self.encode_char, text))

    def decode(self, text):
        if not isinstance(text, str):
            raise Exception("message must be of type string")
        return "".join(map(self.decode_char, text))



class caeser_cipher(base_cipher):
    def __init__(self, c, alphabet=default):
        
        #error checking - the shift c must be an integer
        #the cipher alphabet must be a string it can in theory however contain other characters such as digits or punctuation
        #the cipher alphabet must not contain any repeat characters
        if c != round(c):
            raise Exception("c must be an integer")
        if not isinstance(alphabet, str):
            raise Exception("alphabet must be of type string")
        if len(set(alphabet)) != len(alphabet):
            raise Exception("alphabet must not contain repeat characters")
        
        #setting c between 0-25
        c = c % len(alphabet)
        shifted = f"{alphabet[c::]}{alphabet[:c:]}"
        encode_map = {d: e for d, e in zip(alphabet, shifted)}
        decode_map = {e: d for d, e in zip(alphabet, shifted)}

        self.alphabet = alphabet #so other classes can access the cipher's alphabet
        self.c = c
        

        self._apply_maps(encode_map, decode_map, alphabet)



class affine_cipher(base_cipher):
    def __init__(self, a, b, alphabet=default):
        
        #error checking: a and b must be integers
        if a != round(a) or b != round(b):
            raise Exception("a and b must be integers")
        if not isinstance(alphabet, str):
            raise Exception("alphabet must be of type string")
        if len(set(alphabet)) != len(alphabet):
            raise Exception("alphabet must not contain repeat characters")
        if gcd(a, len(alphabet)) != 1:
            raise Exception("a and the length of the cipher alphabet must be coprime")
        
        #define a lambda function to take an index i -> ai + b
        affine_transform = lambda i: a * i + b
        mapped_indices = map(affine_transform, [i for i in range(len(alphabet))]) #for code readability created this list where indices of the items go to the value of the item itself
        shifted = [alphabet[i%len(alphabet)] for i in mapped_indices]
        encode_map = {d: e for d, e in zip(alphabet, shifted)}
        decode_map = {e: d for d, e in zip(alphabet, shifted)}
        
        self.alphabet = alphabet
        self.a = a #for adding ciphers, we need to access this a to check if they are the same#
        self.b = b

        self._apply_maps(encode_map, decode_map, alphabet)



class substitution_cipher(base_cipher):
    def __init__(self, bijection, alphabet=default):

        #error checking order: must check that both the alphabet and bijection are strings else len() function may give an error
        #checks to see if the bijection is a one-to-one mapping
        if not isinstance(alphabet, str) or not isinstance(bijection, str):
            raise Exception("alphabet must be of type string")
        if len(bijection) != len(alphabet):
            raise Exception("there must be a one-to-one mapping")
        if len(set(bijection)) != len(bijection) or len(set(alphabet)) != len(alphabet):
            raise Exception("there must be a one-to-one mapping")
        
        encode_map = {d: e for d, e in zip(alphabet, bijection)}
        decode_map = {e: d for d, e in zip(alphabet, bijection)}
        
        self.alphabet = alphabet

        self._apply_maps(encode_map, decode_map, alphabet)



class affine_hill_cipher():
    def __init__(self, A, b, alphabet=default):

        

        self.A = np.array(A)
        self.n = self.A.shape[0]
        self.b = np.array(b).reshape(1, -1)
        self.alphabet = alphabet
        self.length = len(alphabet)
        #checks: A must be a square matrix and the number of rows in b must be equal to the number of rows in A, and A must be invertible:
        if self.n != self.A.shape[1]:
            raise Exception("A must be a square matrix")
        if self.b.shape != (1, self.n):
            raise Exception("b must have the same number of rows as A")
        determinant = int(round(np.linalg.det(self.A))) % self.length
        if gcd(determinant, self.length) != 1: #checking for determinant == 0 is not enough for mod determinants
            raise Exception("A must be invertible mod the length of the cipher alphabet")
        
        self.A_inverse = self.matrix_mod_inverse(self.A, self.length)

    
    #both encode and decode block take in a block of size n containing characters, which can be capatilised
    def encode_block(self, block):
        block_indices = np.array([self.alphabet.index(char.lower()) for char in block])
        transformed_indices = ((block_indices @ self.A.T + self.b.flatten()) % self.length)
        encoded_block = [self.alphabet[int(char_index)] if block[i].islower() else self.alphabet[int(char_index)].upper() for i, char_index in enumerate(transformed_indices)]
        return encoded_block
    
    def decode_block(self, block):
        block_indices = np.array([self.alphabet.index(char.lower()) for char in block])
        transformed_indices = ((block_indices - self.b.flatten()) @ self.A_inverse.T) % self.length
        encoded_block = [self.alphabet[int(char_index)] if block[i].islower() else self.alphabet[int(char_index)].upper() for i, char_index in enumerate(transformed_indices)]
        return encoded_block
        
    def matrix_mod_inverse(self, A, m):
        determinant = int(round(np.linalg.det(A)))
        inverse_determinant = pow(determinant, -1, m)
        adjugate = np.round(determinant * np.linalg.inv(A)).astype(int)
        return (inverse_determinant * adjugate) % m


    def encrypt(self, message, decode=False):

        #make a string of all letters in the message that are to be encrypted, and keep track of where these characters originally were in the message so we can add the encrypted characters back in to the same spots later
        positions = []
        for i, char in enumerate(message):
            if char.lower() in self.alphabet:
                positions.append(i)

        text = "".join(char if char.lower() in self.alphabet else "" for char in message)

        #cut off the end block if the length of the characters to be encrypted is not divisble by the block size n
        if not len(text) % self.n == 0:
            text = text[:len(text) - len(text) % self.n:]
            positions = positions[:len(text) - len(text) % self.n:]

        blocks = [text[self.n * i: self.n * i + self.n:] for i in range(int(len(text) / self.n))]

        if decode:
            encoded_characters = np.array([self.decode_block(block) for block in blocks]).flatten().tolist()
        else:
            encoded_characters = np.array([self.encode_block(block) for block in blocks]).flatten().tolist()
        encoded_string = "".join(encoded_characters)

        #build the encrypted message by inserting the encrypted characters along with the characters left unchanged
        encrypted_message = list(message)
        for i, char_index in enumerate(positions):
            encrypted_message[char_index] = encoded_string[i]
        
        return "".join(encrypted_message)


    def compose_affine_hill_cipher(self, cipher):

        #check if all the ciphers have the same alphabet and the same size matrix A, as it is impossible to set constant parameters A and b otherwise.
        length = len(self.alphabet)
        if not isinstance(cipher, affine_hill_cipher):
            raise Exception("cipher inputted must be an affine hill cipher")
        if not cipher.alphabet == self.alphabet:
            raise Exception("cipher inputted must have the same alphabet")
        if not cipher.n == self.n:
            raise Exception("all ciphers must have the same size matrix A")
        determinant = int(round(np.linalg.det(cipher.A))) % length
        if gcd(determinant, length) != 1:
            raise Exception("A must be invertible mod the length of the cipher alphabet")
        
        A = (cipher.A @ self.A) % length
        b = (self.b @ cipher.A.T + cipher.b) % length

        return affine_hill_cipher(A, b, self.alphabet)
    
    def add_affine_hill_cipher(self, cipher):

        #check if all the ciphers have the same alphabet and same matrix A
        length = len(self.alphabet)
        if not isinstance(cipher, affine_hill_cipher):
            raise Exception("cipher inputted must be an affine hill cipher")
        if not cipher.alphabet == self.alphabet:
            raise Exception("cipher inputted must have the same alphabet")
        if not np.array_equal(cipher.A, self.A):
            raise Exception("cipher inputted must have the same matrix A")
        
        b = cipher.b + self.b
        return affine_hill_cipher(self.A, b, self.alphabet)
    
    def scalar_multiply_affine_hill_cipher(self, scalar):
        return affine_hill_cipher(self.A, scalar * self.b, self.alphabet)
        


        







def inverse_cipher(cipher):

    if not isinstance(cipher, base_cipher):
        raise Exception("cipher must inherit a base cipher")

    alphabet = cipher.alphabet

    if isinstance(cipher, caeser_cipher):
        return caeser_cipher(-cipher.c, alphabet)
    if isinstance(cipher, affine_cipher):
        a = pow(cipher.a, -1, len(alphabet))
        b = (a * cipher.b) % len(alphabet)
        return affine_cipher(a, b, alphabet)

    encrypted_alphabet = cipher.encode(alphabet)
    return substitution_cipher(encrypted_alphabet, alphabet)  


def compose_ciphers(*ciphers):

    if len(ciphers) == 0:
        raise Exception("there must be at least one cipher to compose") #check whether all of the items in the list are valid ciphers
    for cipher in ciphers:
        if not isinstance(cipher, base_cipher):
            raise Exception("every item inputted must be a cipher")

    alphabet = ciphers[0].alphabet

    #check if all the inputted ciphers are caeser ciphers and they share the same alphabet, in which case the composed cipher will also be part of the caeser cipher class. Same with affine ciphers
    if all(alphabet == cipher.alphabet for cipher in ciphers):
        if all(isinstance(cipher, caeser_cipher) for cipher in ciphers):
            c = sum(cipher.c for cipher in ciphers)
            return caeser_cipher(c, alphabet)
    
        if all(isinstance(cipher, affine_cipher) for cipher in ciphers):
            a, b = 1, 0
            for cipher in ciphers:
                a *= cipher.a
                b = b * cipher.a + cipher.b
            return affine_cipher(a, b, alphabet)
    #create a union of every alphabet in the ciphers to be composed
    alphabet = "".join(sorted(set("".join(cipher.alphabet for cipher in ciphers))))
    encrypted_alphabet = alphabet
    for cipher in ciphers:
        encrypted_alphabet = cipher.encode(encrypted_alphabet) #create an encrypted alphabet which acts as the bijection exactly like the logic in the substitution cipher class
    return substitution_cipher(encrypted_alphabet, alphabet)

    



def power_cipher(cipher, power):
        
    #check that a valid cipher has been inputted and an integer has been inputted as the power
    if not isinstance(cipher, base_cipher):
        raise Exception("cipher must inherit a base cipher")
    if not isinstance(power, int):
        raise Exception("power must be an integer")
    
    alphabet = cipher.alphabet

    #I have defined a power of 0 to return the identity cipher, and a negative power -n to decode the message n times rather than encoding it n times
    if power != 0:
        if power > 0:
            return compose_ciphers(*[cipher]*power)
        else:
            return compose_ciphers(*[inverse_cipher(cipher)]*abs(power))
    else:
        return substitution_cipher(alphabet, alphabet) #the identity cipher
        



def add_ciphers(*ciphers):

    #addition is only defined on ciphers of the same class, and only defined on either caeser or affine ciphers. Addition is also only defined when all the ciphers inputted share the same cipher alphabet. On affine ciphers they all must have the same multiplier a
    if len(ciphers) == 0:
        raise Exception("there must be at least one cipher to compose")
    if type(ciphers[0]) not in [caeser_cipher, affine_cipher]:
        raise Exception("all the ciphers must be caeser or affine ciphers")
    cipher_class = type(ciphers[0])
    alphabet = ciphers[0].alphabet
    if not all(isinstance(cipher, cipher_class) for cipher in ciphers):
        raise Exception("all of the ciphers must be of the same class")
    if not all(cipher.alphabet == alphabet for cipher in ciphers):
        raise Exception("all of the ciphers must have the same cipher alphabet")
    if cipher_class == affine_cipher:
        a = ciphers[0].a
        if not all(cipher.a == a for cipher in ciphers):
            raise Exception("all affine ciphers must have the same mulptiplier a")

    #for a caeser ciphers, adding them together is the same as composing them
    encrypted_alphabet = alphabet
    if cipher_class == caeser_cipher:
        c = sum(cipher.c for cipher in ciphers)
        return caeser_cipher(c, alphabet)
    if cipher_class == affine_cipher: #for affine ciphers, adding them together means adding the bs together and keeping the multiplier a the same
        b = sum(cipher.b for cipher in ciphers)
        return affine_cipher(a, b, alphabet)
        



def scalar_multiply_cipher(cipher, scalar):

    if type(cipher) not in [caeser_cipher, affine_cipher]:
        raise Exception("only caeser and affine ciphers can be scalar multiplied")
    if not isinstance(scalar, int):
        raise Exception("scalar mulptiplier must be an integer")
        
    alphabet = cipher.alphabet

    if isinstance(cipher, caeser_cipher):
        return caeser_cipher(cipher.c * scalar, alphabet)
    if isinstance(cipher, affine_cipher):
        return affine_cipher(cipher.a, cipher.b * scalar, alphabet)
        
        



def split(alphabet:str):
    l = len(alphabet)
    return f"{alphabet[::2]}{alphabet[l-(l%2*2)::-2]}"

def reverse(alphabet:str):
    return alphabet[::-1]



def print_messages(cipher, messages):
    for message in messages:
        encoded = cipher.encode(message)
        print(f"original message: {message}")
        print(f"encoded message: {encoded}")
        print(f"decoded message: {cipher.decode(encoded)}", end="\n\n")



c_three = caeser_cipher(3)
c_minus_five = caeser_cipher(-5)
c_two = caeser_cipher(2)

a_eight_five = affine_cipher(9, 5)
a_seven_three = affine_cipher(7, 3)
a_three_five = affine_cipher(3, 5)
a_two_five_vowels = affine_cipher(2, 5, vowels)
c_seven_ambidextrous = caeser_cipher(7, ambidextrous)

ah_vowels = affine_hill_cipher([[2, 1], [1, 1]], [1, 0])
ah_vowels_2 = affine_hill_cipher([[3, 2], [0, 1]], [1, 2])
ah_vowels_3 = affine_hill_cipher([[2, 1], [1, 1]], [2, 3])
ah_mixture = ah_vowels.scalar_multiply_affine_hill_cipher(4)
encoded_message = ah_mixture.encrypt(bond)
print(encoded_message)
print(ah_mixture.encrypt(encoded_message, True))















