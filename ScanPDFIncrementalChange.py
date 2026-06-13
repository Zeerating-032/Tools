import os, pikepdf

TARGET_FOLDER = "D:/NTU class/06_3-2/"
REPLACE_SAVE = True # 直接覆蓋原檔
if REPLACE_SAVE:
    DESTINATION_FOLDER = TARGET_FOLDER
else:
    DESTINATION_FOLDER =TARGET_FOLDER + "_new"
# 只掃描檔尾多少 bytes
TAIL_SIZE = 4 * 1024 * 1024  # 4 MB
# 幾個EOF以上要重新存
EOF_CRITERIA = 3

def Count_EOF_Markers(pdf_path: str, tail_size: int = TAIL_SIZE):
    file_size = os.path.getsize(pdf_path)
    read_size = min(file_size, tail_size)
    with open(pdf_path, "rb") as f:
        f.seek(file_size - read_size)
        data = f.read(read_size)

    eof_count = data.count(b"%%EOF")
    return eof_count

def Re_Save_PDF(pdf_path: str):
    # 輸出位置只改母資料夾，檔名維持
    relative_path = os.path.relpath(pdf_path, TARGET_FOLDER)
    output_path = os.path.join(DESTINATION_FOLDER, relative_path)
    Destination_Folder = os.path.split(output_path)[0]
    if not os.path.exists(Destination_Folder):
        os.makedirs(Destination_Folder, 0o777, exist_ok=True)

    try:
        # 開啟並重新保存
        with pikepdf.open(pdf_path, allow_overwriting_input = True) as pdf:
            pdf.save(output_path)
        print(f"[成功] 重新儲存：{output_path}")
    except Exception as e:
        print(f"[錯誤] 無法處理 {pdf_path}：{e}")

def Scan_PDF_DFS(path: str):
    """
    或許可以用os.walk改寫
    """
    AllContentList = os.listdir(path)
    FolderList = []
    PdfList = []
    for i in AllContentList:
        a = os.path.join(path, i)
        if os.path.islink(a): # GPT: 以免無限輪迴
            continue
        elif os.path.isdir(a):
            FolderList.append(a)
        else: # file
            name, ext = os.path.splitext(a)
            if ext.lower() == ".pdf":
                PdfList.append(a)
            else:
                pass
    for FurtherPath in FolderList:
        Scan_PDF_DFS(FurtherPath)
    
    for Pdf in PdfList:
        EofNum = Count_EOF_Markers(Pdf)
        if EofNum >= EOF_CRITERIA:
            print (f"[EOF:{EofNum}] {Pdf}")
            Re_Save_PDF(Pdf)
        else:
            print(f"[略過] {Pdf}")

def Scan_PDF_WALK():
    """
    os.walk改寫
    """
    AllContent = os.walk(TARGET_FOLDER)
    for root, folders, files in AllContent:
        for file in files:
            a = os.path.join(root, file)
            name, ext = os.path.splitext(a)
            if ext.lower() != ".pdf":
                continue
            EofNum = Count_EOF_Markers(a)
            if EofNum >= EOF_CRITERIA:
                print (f"[EOF:{EofNum}] {a}")
                Re_Save_PDF(a)
            else:
                pass
                # print(f"[略過] {a}")

if __name__ == "__main__":
    Scan_PDF_WALK()
