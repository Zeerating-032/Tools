import tkinter as tk
from tkinter import ttk
import threading
import time
from pycaw.pycaw import AudioUtilities

# 未完成: 靜音不會偵測到

# 音量調整
def get_volume():
    '''
    取得音量值
    '''
    device = AudioUtilities.GetSpeakers()
    return device.EndpointVolume.GetMasterVolumeLevelScalar()

def set_volume(value):
    '''
    設定音量值
    '''
    device = AudioUtilities.GetSpeakers()
    device.EndpointVolume.SetMasterVolumeLevelScalar(max(0, min(1, value)), None)

# 全域狀態
fading = False
fade_thread = None

# 顯示更新
def update_display():
    global fading
    vol = round(get_volume() * 100)
    volume_label.config(
        text=f"音量：{vol}",
        foreground="red" if fading else "black"
    )
    root.after(100, update_display)

# 功能1: 漸弱
def start_fade():
    global fading
    if fading:
        return
    # 取得秒數、頻率和初音量
    try:
        seconds = float(fade_time_entry.get())
        if seconds <= 0:
            return
    except:
        seconds = 2
    try:
        frequency = float(fade_frequency_entry.get())
        if frequency <= 0:
            return
    except:
        frequency = 2
    start_volume = get_volume()
    if start_volume <= 0:
        return
    # 相對於啟動時間調整音量
    start_time = time.perf_counter()

    # 離開漸弱狀態時執行
    def end_fade():
        global fading
        fading = False
        fade_button.config(state = "normal")

    # 進入漸弱狀態
    fading = True
    fade_button.config(state = "disabled")
    def fade():
        global fading
        
        # Windows系統要求初始化COM
        import comtypes
        comtypes.CoInitialize()
        # 先cache裝置會比較穩
        device = AudioUtilities.GetSpeakers()
        endpoint = device.EndpointVolume
        
        steps = int(seconds * frequency)
        if steps < 1:
            steps = 1
        last_set = start_volume # 上一次程式修改成的音量，用於人工干預檢測
        
        while 1:
            # 例如回復功能應中斷漸弱
            if not fading: 
                comtypes.CoUninitialize()
                end_fade()
                return
            # 外部調整偵測，若有人為控制就中止漸弱
            current = endpoint.GetMasterVolumeLevelScalar()
            if abs(current - last_set) > 0.015:
                comtypes.CoUninitialize()
                end_fade()
                return
            # 進度量
            elapsed = time.perf_counter() - start_time
            # 完成就離開
            if elapsed >= seconds:
                break
            # 修改音量
            new_volume = start_volume * (1 - elapsed / seconds)
            set_volume(new_volume)
            last_set = new_volume
            time.sleep(1/frequency)

        # 最終確認歸零和中止狀態
        set_volume(0)
        comtypes.CoUninitialize()
        end_fade()

    # 用threading以免中間的休息使GUI無回應
    threading.Thread(target=fade, daemon=True).start()

# 功能2: 回復
def restore_volume():
    global fading
    # 會直接中斷漸弱
    fading = False
    try:
        value = float(restore_entry.get())
    except:
        value = 100
    set_volume(value / 100)

# GUI
root = tk.Tk()
root.title("Audio Fade Tool")
root.geometry("220x320")

# 8格 grid
for i in range(2):
    root.columnconfigure(i, weight = 1)
for i in range(4):
    root.rowconfigure(i, weight = 1)

# (0, 0~1)：顯示
volume_label = tk.Label(root, text="音量：0", font=("Arial", 16))
volume_label.grid(row=0, column=0, columnspan=2)
# (1, 0)：漸弱按鈕
fade_button = ttk.Button(root, text="漸弱(秒)", command=start_fade)
fade_button.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
# (1, 1)：秒數
fade_time_entry = ttk.Entry(root, justify="center")
fade_time_entry.insert(0, "2")
fade_time_entry.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)
# (2, 1)：回復
restore_button = ttk.Button(root, text="回復(值)", command=restore_volume)
restore_button.grid(row=2, column=0, sticky="nsew", padx=5, pady=5)
# (2, 2)：回復值
restore_entry = ttk.Entry(root, justify="center")
restore_entry.insert(0, "100")
restore_entry.grid(row=2, column=1, sticky="nsew", padx=5, pady=5)
# (3, 1)：每秒更新
fade_frequency_label = tk.Label(root, text="頻率(1/秒)")
fade_frequency_label.grid(row=3, column=0, sticky="nsew", padx=5, pady=5)
# (3, 2)：每秒更新值
fade_frequency_entry = ttk.Entry(root, justify="center")
fade_frequency_entry.insert(0, "2")
fade_frequency_entry.grid(row=3, column=1, sticky="nsew", padx=5, pady=5)

# 開始更新
update_display()
root.mainloop()