import json, os, re

bili_dir = "/storage/emulated/0/Android/data/com.bilibili.app.in/download/"
out_root_dir = "./output/"
if not os.path.exists(out_root_dir):
    os.mkdir(out_root_dir)

# all_data = 
# {
#   title1:
#      [
#          {page:, part:, media_type:, media_fdr:}, 
#          {page:, part:, media_type:, media_fdr:},
#      ],
#   title2:
# }

all_data = {}
def dfs(dir): # 找出所有符合格式的資料夾建立資料
    global all_data
    content = os.listdir(dir)
    if "entry.json" not in content: # 向下遞迴
        for i in content:
            fullpath = os.path.join(dir, i)
            if os.path.isdir(fullpath):
                dfs(fullpath)
    else:
        # json提取，用title, page, part
        entry = json.load(open(os.path.join(dir, "entry.json")))

        # 檢查影片資料夾格式
        media_fdr = []
        for i in content:
            if os.path.isdir(os.path.join(dir, i)):
                media_fdr.append(os.path.join(dir, i)) # 應該只有一個資料夾，存放影音檔

        if len(media_fdr) != 1: # 影片資料夾格式不合
            print(f"資料夾 {dir[len(bili_dir):]} 有entry.json但影片資料夾不合格式")
            return
        else:
            # 檢查影片格式 (m4s/blv)
            media_fdr = media_fdr[0]
            blv_check = lambda x: bool(re.match("^index\.json$|^[\d]+\.blv$", x))
            if {"video.m4s", "audio.m4s"} <= set(os.listdir(media_fdr)):
                media_type = "m4s"
            elif all(filter(blv_check, os.listdir(media_fdr))):
                media_type = "blv"
            else:
                print(f"資料夾{dir[len(bili_dir):]}影片格式無法判定")
        
        # 輸入資料
        entry["title"] = entry["title"].replace("/", "_") # 避免檔名有/
        if entry["title"] not in list(all_data.keys()):
            all_data[entry["title"]] = []
        segment = {
            "page": entry["page_data"]["page"], 
            "part": entry["page_data"]["part"], 
            "media_type": media_type, 
            "media_fdr": media_fdr
        }
        all_data[entry["title"]].append(segment)

def mixup(out_dir, data):
    all_page = set()
    ignore_page = set()
    has_output = os.listdir(out_dir)
    data = sorted(data, key = lambda x: int(x["page"]))

    # 輸出影片集資料、收集已輸出影片
    for part in data:
        print(part["page"], part["part"])
        all_page.add(part["page"])
        if part["part"]+".mp4" in has_output:
            ignore_page.add(part["page"])
    print("已輸出影片編號，不再輸出:", ignore_page)
    
    # 手動忽略
    user_ignore = []
    a = input("手動忽略編號(ex. 1-4,7): ")
    for seg in a.split(","):
        if len(seg) == 0:
            continue
        elif "-" not in seg:
            user_ignore.append(int(seg))
        else:
            b = list(map(int, seg.split("-")))
            user_ignore.extend(list(range(b[0], b[1]+1)))
    # 計算實際合併標號
    mix_pages = all_page - ignore_page - set(user_ignore)

    #執行合併
    for part in data:
        if part["page"] not in mix_pages:
            continue
        merge(part["media_type"], out_dir, part["part"], part["media_fdr"])

def merge(typ, out_dir, name, media_fdr):
    if typ == "m4s":
        vid = os.path.join(media_fdr, "video.m4s")
        aud = os.path.join(media_fdr, "audio.m4s")
        name = name.replace("/", "&") # 避免被視為資料夾層
        os.system(
            f'ffmpeg -hide_banner -loglevel info -y -i "{vid}" -i "{aud}" -c:a copy -c:v copy "{os.path.join(out_dir, name)}".mp4'
        )
    
    elif typ == "blv":
        leave = 0
        n = sum(map(lambda x: x.endswith(".blv"), os.listdir(media_fdr)))
        with open("temp.txt", "w") as f:
            for i in range(n):
                if f"{i}.blv" in os.listdir(media_fdr):
                    full = os.path.join(media_fdr, f"{i}.blv")
                    f.write(f"file '{full}'\n")
                else:
                    print("影片{name}錯誤, 缺少{i}.blv")
                    leave = 1
                    break
        if not leave:
            os.system(
                f'ffmpeg -safe 0 -f concat -i temp.txt -c copy "{os.path.join(out_dir, name)}.mp4"'
            )
        os.remove("temp.txt")

    else:
        print(f"影片種類{typ}無合併方法設定")

if __name__ == "__main__":
    dfs(bili_dir)

    for episode, data in all_data.items():
        out_dir = out_root_dir + episode
        if not os.path.exists(out_dir):
            os.mkdir(out_dir)
        mixup(out_dir, data)
