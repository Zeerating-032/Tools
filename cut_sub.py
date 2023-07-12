#將一段srt字幕平移一段時間，轉成ms計算後再回去一般的格式
#沒有小時

previous = open("./sub0.txt", "r", encoding = "utf8")
finish = open("./fini.txt", "w", encoding = "utf8")

order = [str(i) for i in range(300, 0, -1)]
text = previous.readlines()
print(len(text))

def to_ms(t):
	t = t.split(":")
	k = t[1].split(",")
	return int(t[0])*60000 + int(k[0])*1000 + int(k[1])

def to_time(ms):
	min = str(ms // 60000)
	ms = ms % 60000
	sec = str(ms // 1000)
	ms = str(ms % 1000)
	
	out = "00:"
	for x, y in zip((min, sec), (2, 2)):
		out += "0"*(y-len(x)) + x + ":"
	out = out[:-1] + "," + "0"*(3-len(ms)) + ms 
	return out
		
		
cut_time = input("You want to cut {mm:ss,xxx}:")
cut_ms = to_ms(cut_time)

while len(text) != 0:
	pre_order = text.pop(0) #useless
	duration = text.pop(0).strip()
	subtitle = ""
	inp = "meaningless"
	while len(inp) != 1:
		inp = text.pop(0)
		subtitle += inp
	
	start, end = tuple(duration.split(" --> "))
	start, end = start[3:], end[3:]
	new_start_ms = to_ms(start) - cut_ms
	new_end_ms = to_ms(end) - cut_ms
	new_start = to_time(new_start_ms)
	new_end = to_time(new_end_ms)
	
	new_duration = new_start + " --> " + new_end
	
	print(order.pop(), file = finish)
	print(new_duration, file = finish)
	print(subtitle[:-1], file = finish)

previous.close()
finish.close()