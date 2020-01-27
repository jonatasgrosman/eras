#Decorators
def returnHeaderIndex(f):
	def decorated_function(*args, **kwargs):
		fun_ret = f(*args, **kwargs)
		index_dict = {}
		headers = fun_ret[0]
		index_dict = {headers[i]:i for i in range(len(headers))}
		return fun_ret, index_dict
	return decorated_function