
address = [i['addr'] for i in ifaddresses(interfaces()[-2]).setdefault(AF_INET6, [{'addr': 'No IP addr'}])][-1]
print(address)
