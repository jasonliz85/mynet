#!pythonpath

test2 = '224.208.37.138'
find_point = test2.find('.')

while (find_point > -1):
	find_point = test2.find('.')
	ip_normal = test2[0:find_point] + ip_normal
	test2 = test2.replace(test2[0:find_point], '')
	test2 = test2.lstrip('.')
	print test2
