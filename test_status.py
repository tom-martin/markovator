import file_system_status as status

s = {}
s['reply_since_id'] = '123'
status.save(s)
s = status.load()
assert s['reply_since_id']  == '123'
status.clear()
s = status.load()
assert 'reply_since_id' not in s
print("Tests passed")