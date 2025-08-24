import json, os, re

# Android 11+, termux無法存取Android/data, 須先複製一份
# 下載影片的資料夾 "/storage/emulated/0/Android/data/com.bilibili.app.in/download/"
# 可用subprocess或shlex處理檔名問題
BILI_FOLDER ="../bili_raw/"
OUTPUT_FOLDER = "../output/"
if not os.path.exists(OUTPUT_FOLDER):
    os.mkdir(OUTPUT_FOLDER)
RP_LIST = [
    ("/", "&"),
    ("*", ""),
    (":", " "),
    ("'", " ")
]
DEL_LIST = []
OUTPUT_NAME_WITH_ORDER = 0 # 將輸出檔名從part改成page_part, 與檢查已輸出有關

def replace_string(x: str) -> str:
    '''
    替換RP_LIST中的字元, 避免特殊字元報錯
    刪掉DEL_LIST中的字元
    '''
    for a, b in RP_LIST:
        x = x.replace(a, b)
    for i in DEL_LIST:
        x = x.replace(i, "")
    return x

all_data = dict()
def collect_vid(root_folder: str) -> None:
    '''
    DFS方法從root_folder向下找個別影片資料夾, 存進all_data
    all_data = 
    {
    title1:
        [
            {page:, part:, media_type:, media_fdr:, name:}, 
            {page:, part:, media_type:, media_fdr:, name:},
        ],
    title2:
    }
    '''
    global all_data
    if os.path.isfile(os.path.join(root_folder, "entry.json")):
        # 正確格式中只會有一個裝影音檔的資料夾, 直接指定
        media_folder = next(os.walk(root_folder))[1][0]
        media_folder = os.path.join(root_folder, media_folder)
        # 檢查m4s/blv格式
        blv_check = lambda x: bool(re.match(r"^index\.json$|^[\d]+\.blv$", x))
        if {"video.m4s", "audio.m4s"} <= set(os.listdir(media_folder)):
            media_type = "m4s"
        elif all(filter(blv_check, os.listdir(media_folder))):
            media_type = "blv"
        else:
            print(f"資料夾{root_folder}: 影片格式無法判定")
        # 提取資料, 需要title, page, part
        entry = json.load(open(os.path.join(root_folder, "entry.json")))
        segment = {
            "page": entry["page_data"]["page"], # 序數
            "part": replace_string(entry["page_data"]["part"]), # 子名稱
            "media_type": media_type, 
            "media_fdr": media_folder
        }
        # 檔名是否加序號
        if OUTPUT_NAME_WITH_ORDER:
            segment["name"] = f'{segment["page"]}_{segment["part"]}.mp4'
        else:
            segment["name"] = segment["part"]+".mp4"
        # 母名稱與歸檔
        title = replace_string(entry["title"]) # 母名稱
        if title not in list(all_data.keys()):
            all_data[title] = []
        all_data[title].append(segment)
        return

    else:
        # 向下遞迴
        children_folder = next(os.walk(root_folder))[1]
        for i in children_folder:
            collect_vid(os.path.join(root_folder, i))
        return

def merge(out_fdr: str, subvid: list, exec_order: set[int]):
    '''
    out_fdr: 輸出的資料夾, 包含母名稱資訊
    subvid: 母名稱下的子影片資訊
    exec_order: 需要合併的序號(part)集合
    '''
    for v in subvid:
        # 忽略
        if v["page"] not in exec_order:
            continue
        
        # 合併: m4s模式
        if v["media_type"] == "m4s":
            vid = os.path.join(v["media_fdr"], "video.m4s")
            aud = os.path.join(v["media_fdr"], "audio.m4s")
            name = os.path.join(out_fdr, v["name"])
            os.system(
                f"ffmpeg -hide_banner -loglevel info -y -i '{vid}' -i '{aud}' -c:a copy -c:v copy '{name}'"
            )
        
        # 合併: blv模式
        elif v["media_type"] == "blv":
            leave = 0
            n = sum(map(lambda x: x.endswith(".blv"), os.listdir(v["media_fdr"])))
            with open("temp.txt", "w") as f:
                for i in range(n):
                    if f"{i}.blv" in os.listdir(v["media_fdr"]):
                        full = os.path.join(v["media_fdr"], f"{i}.blv")
                        f.write(f"file '{full}'\n")
                    else:
                        print("影片{name}錯誤, 缺少{i}.blv")
                        leave = 1
                        break
            if not leave:
                name = os.path.join(out_fdr, v["name"])
                os.system(
                    f"ffmpeg -hide_banner -loglevel info -f concat -safe 0 -i temp.txt -c copy '{name}'"
                )
            os.remove("temp.txt")


if __name__ == "__main__":
    collect_vid(BILI_FOLDER)
    for work, seg in all_data.items():
        output_fdr = os.path.join(OUTPUT_FOLDER, work)
        if not os.path.isdir(output_fdr):
            os.mkdir(output_fdr)
        seg = sorted(seg, key = lambda x: int(x["page"]))
        
        # 收集已輸出影片 # output_fdr必存在 可改
        if os.path.isdir(output_fdr):
            has_output_name = set(map(lambda x: str(x["name"]), seg)) & set(os.listdir(output_fdr))
            has_output_page = []
            for i in seg:
                if i["name"] in has_output_name:
                    has_output_page.append(i["page"])
        else:
            has_output_page = []
        
        # 列出作品名
        print(work)
        for vid in seg:
            # 子影片序號名稱
            print(vid["page"], vid["part"])
            # 收集已輸出影片
        print("已輸出影片編號，不再輸出:", has_output_page)

        # 輸入手動忽略
        user_ignore = []
        a = input("手動忽略編號(ex. 1-4,7): ")
        for i in a.split(","):
            if len(i) == 0:
                continue
            elif "-" not in i:
                user_ignore.append(int(i))
            else:
                b = list(map(int, i.split("-")))
                user_ignore.extend(list(range(b[0], b[1]+1)))
        
        # 計算實際合併標號
        all_page = set(map(lambda x: int(x["page"]), seg))
        merge_page = all_page - set(has_output_page) - set(user_ignore)

        # 執行合併
        merge(output_fdr, seg, merge_page)
