# -*- coding: utf8 -*-

class Bitarray:
    def __init__(self, size):
        """ Create a bit array of a specific size """
        self.size = size
        self.bitarray = bytearray(size/8+1)

    def set(self, n):
        """ Sets the nth element of the bitarray """

        index = n / 8
        position = n % 8
        self.bitarray[index] = self.bitarray[index] | 1 << (7 - position)

    def get(self, n):
        """ Gets the nth element of the bitarray """
        
        index = n / 8
        position = n % 8
        return (self.bitarray[index] & (1 << (7 - position))) > 0 

def BKDRHash(the_seed,key):
    seed = the_seed # 31 131 1313 13131 131313 etc..
    hash = 0
    for i in range(len(key)):
      hash = (hash * seed) + ord(key[i])
    return hash

class BloomFilter:
	def __init__(self, m, k):
		self.bitset = Bitarray(m)
		self.k = (k if k<=10 else 10)
		self.m = m
		self.seed = [31, 131, 1313, 13131, 131313, 1313131, 13131313, 131313131, 1313131313, 1313131313]

	def set(self, key):
		for i in range(self.k):
			value = BKDRHash(self.seed[i], key)%(self.m)
			self.bitset.set(value)

	def check(self, key):
		for i in range(self.k):
			value = BKDRHash(self.seed[i], key)%(self.m)
			if(not self.bitset.get(value)):
				return False
		return True


if __name__ == '__main__':
	test_file = open('45094.txt')
	words = test_file.read().splitlines()
	test_file.close()

	def false_positive_rate(filter):
		cnt = 0
		for word in words:
			if(filter.check(word)):
				cnt += 1
			else:
				filter.set(word)
		return (cnt/45094.0)

	for i in range(2,10):
		for j in range(2,10):
			print false_positive_rate(BloomFilter(45094*i, j))