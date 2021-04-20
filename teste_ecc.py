# Plutus Bitcoin Brute Forcer
# Made by Isaac Delly
# https://github.com/Isaacdelly/Plutus

from ellipticcurve.privateKey import PrivateKey

# import sqlite3
import os
import pickle
import hashlib
import binascii
import multiprocessing
import psycopg2
import re
import time

"""
habilitar para comunicacao ao banco
"""
conn = psycopg2.connect(
	'host=host.docker.internal port=5432 dbname=bitcoin user=postgres password=1234')
conn.autocommit = True

select_ = """select * from balance where address = ?"""

insert_ = """insert into address (address,private_key,public_key) values (%s,%s,%s)"""


def generate_private_key():
	"""
	Generate a random 32-byte hex integer which serves as a randomly
	generated Bitcoin private key.
	Average Time: 0.0000061659 seconds
	"""
	return binascii.hexlify(os.urandom(32)).decode('utf-8').upper()


def private_key_to_public_key(private_key):
	"""
	Accept a hex private key and convert it to its respective public key.
	Because converting a private key to a public key requires SECP256k1 ECDSA
	signing, this function is the most time consuming and is a bottleneck in
	the overall speed of the program.
	Average Time: 0.0031567731 seconds
	"""
	pk = PrivateKey().fromString(bytes.fromhex(private_key))
	public = pk.publicKey().toString().hex().upper()

	return '04' + public


def public_key_to_address(public_key):
	"""
	Accept a public key and convert it to its resepective P2PKH wallet address.
	Average Time: 0.0000801390 seconds
	"""
	output = []
	alphabet = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
	var = hashlib.new('ripemd160')
	encoding = binascii.unhexlify(public_key.encode())
	var.update(hashlib.sha256(encoding).digest())
	var_encoded = ('00' + var.hexdigest()).encode()
	digest = hashlib.sha256(binascii.unhexlify(var_encoded)).digest()
	var_hex = '00' + var.hexdigest() + hashlib.sha256(digest).hexdigest()[0:8]
	count = [char != '0' for char in var_hex].index(True) // 2
	n = int(var_hex, 16)
	while n > 0:
		n, remainder = divmod(n, 58)
		output.append(alphabet[remainder])
	for i in range(count):
		output.append(alphabet[0])
	return ''.join(output[::-1])

def private_key_to_WIF(private_key):
	"""
	Convert the hex private key into Wallet Import Format for easier wallet
	importing. This function is only called if a wallet with a balance is
	found. Because that event is rare, this function is not significant to the
	main pipeline of the program and is not timed.
	"""
	digest = hashlib.sha256(binascii.unhexlify('80' + private_key)).hexdigest()
	var = hashlib.sha256(binascii.unhexlify(digest)).hexdigest()
	var = binascii.unhexlify('80' + private_key + var[0:8])
	alphabet = chars = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
	value = pad = 0
	result = ''
	for i, c in enumerate(var[::-1]):
		value += 256**i * c
	while value >= len(alphabet):
		div, mod = divmod(value, len(alphabet))
		result, value = chars[mod] + result, div
	result = chars[value] + result
	for c in var:
		if c == 0:
			pad += 1
		else:
			break
	return chars[0] * pad + result


def to_csv(private, public, wallets):
	private_salvar = str(private)
	public_salvar = str(public)
	wallets_salvar = str(wallets)

	txt_salvar = private_salvar + ';' + public_salvar + ';' + wallets_salvar + '\n'

	with open('wallets_generated.csv', 'a+') as f:
		f.write(txt_salvar)
	f.close()

	# 	cur.execute('INSERT INTO wallets (private_key,words,address) VALUES (%s,%s,%s)',(private_key,wif,address))
	# 	conn.commit()


def to_query(private='', public='', wallets='', procedure=None):
	try:
		curr = conn.cursor()

		# if procedure:
		# 	curr.execute('call verify();')
		# 	return
		private_salvar = str(private)
		public_salvar = str(public)
		wallets_salvar = str(wallets)

		# curr.execute(select_, (wallets_salvar,))

		# if curr.fetchone() != None:
		curr.execute(insert_, (wallets_salvar, private_salvar, public_salvar,))
		# conn.commit()

	except:
		raise Exception

	finally:
		curr.close()


def main():
	"""
	Create the main pipeline by using an infinite loop to repeatedly call the
	functions, while utilizing multiprocessing from __main__. Because all the
	functions are relatively fast, it is better to combine them all into
	one process.
	"""
	print('Starting' + '\n')
	while True:
		# for i in range(0, 1000000):
		try:

			private_key = generate_private_key()			# 0.0000061659 seconds
			public_key = private_key_to_public_key(
				private_key) 	# 0.0031567731 seconds
			address = public_key_to_address(public_key)		# 0.0000801390 seconds

			# to_csv(private_key, public_key, address)
			to_query(private_key, public_key, address)
		except Exception as e:
# 			print(e.message)
# 			conn.close()
			break


if __name__ == '__main__':
	"""
	Deserialize the database and read into a list of sets for easier selection 
	and O(1) complexity. Initialize the multiprocessing to target the main 
	function with cpu_count() concurrent processes.
	"""
	# database = [set() for _ in range(4)]
	# count = len(os.listdir(DATABASE))
	# half = count // 2
	# quarter = half // 2
	# for c, p in enumerate(os.listdir(DATABASE)):
	# 	print('\rreading database: ' + str(c + 1) + '/' + str(count), end = ' ')
	# 	with open(DATABASE + p, 'rb') as file:
	# 		if c < half:
	# 			if c < quarter: database[0] = database[0] | pickle.load(file)
	# 			else: database[1] = database[1] | pickle.load(file)
	# 		else:
	# 			if c < half + quarter: database[2] = database[2] | pickle.load(file)
	# 			else: database[3] = database[3] | pickle.load(file)

	# To verify the database size, remove the # from the line below
	# print('database size: ' + str(sum(len(i) for i in database))); quit()

	for cpu in range(4):
		multiprocessing.Process(target=main, args=()).start()

	# main()
