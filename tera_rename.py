import os

dir_start = "義"
dir_path = "/storage/emulated/0/00_SELF/"
a = list(filter(lambda x: x.startswith(dir_start), os.listdir(dir_path)))[0]
print("修改：", a)
dir_path += a + "/"

for i in os.listdir(dir_path):
    os.rename(dir_path + i, dir_path + i[:-1])

print("完成")