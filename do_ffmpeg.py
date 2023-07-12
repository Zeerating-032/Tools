import os

'''
Put those files you want to covert in
/storage/emulated/0/Music/before
'''

dir_name = "/storage/emulated/0/Music/before/"
end_dir = "/storage/emulated/0/Music/after/"
file_name = os.listdir(dir_name)
if not os.path.exists(end_dir):
    os.mkdir(end_dir)

def re_m4a_mp3(i):
	if i.endswith(".m4a"):
		j = i.replace(".m4a", ".mp3")
		return f"ffmpeg -hide_banner -i '{dir_name}{i}' -b:a 128K '{end_dir}{j}'"
	else:
		print ("IGNORE", i)

def ex_mp4_m4a(i):
	if i.endswith(".mp4"):
		j = i.replace(".mp4", ".m4a")
		return f"ffmpeg -hide_banner -i '{dir_name}{i}' -vn -c:a copy '{end_dir}{j}'"
	else:
		print ("IGNORE", i)


DO = ex_mp4_m4a
for i in file_name:
	comm = DO(i)
	if comm is not None:
		os.system(comm)
print ("Finish all")