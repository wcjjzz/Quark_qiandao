import os
import requests
import traceback

def sign_once(kps, sign, vcode, alias):
    """
    单账号签到逻辑
    """
    try:
        headers = {
            "Cookie": f"QUARK_KPS={kps}; QUARK_SIGN={sign}; QUARK_VCODE={vcode}",
            "User-Agent": "okhttp/3.12.12"
        }
        url = "https://drive-m.quark.cn/1/clouddrive/capacity/growth/sign_in"
        resp = requests.post(url, headers=headers)
        data = resp.json()
        if data.get("code") == 0:
            return True, f"{alias} 签到成功，获得 {data.get('data', {}).get('capacity', '未知')} 容量"
        else:
            return False, f"{alias} 签到失败，返回：{data}"
    except Exception as e:
        return False, f"{alias} 异常：{e}\n{traceback.format_exc()}"

def main():
    # 支持三种方式：
    # 1. QUARK_ACCOUNTS （多行：kps,sign,vcode）
    # 2. 传统三个变量（用逗号分隔）
    accounts_env = os.getenv("QUARK_ACCOUNTS", "").strip()
    accounts = []

    if accounts_env:
        # 多行格式
        lines = [ln.strip() for ln in accounts_env.splitlines() if ln.strip()]
        for i, ln in enumerate(lines, 1):
            parts = [x.strip() for x in ln.split(",")]
            if len(parts) < 3:
                raise ValueError(f"第 {i} 行格式错误，应为 kps,sign,vcode")
            accounts.append((parts[0], parts[1], parts[2], f"Account#{i}"))
    else:
        # 三个变量逗号分隔
        kps_list = os.getenv("QUARK_KPS", "").split(",")
        sign_list = os.getenv("QUARK_SIGN", "").split(",")
        vcode_list = os.getenv("QUARK_VCODE", "").split(",")
        if not (len(kps_list) == len(sign_list) == len(vcode_list)):
            raise ValueError("QUARK_KPS/QUARK_SIGN/QUARK_VCODE 数量不一致")
        for i in range(len(kps_list)):
            accounts.append((kps_list[i].strip(), sign_list[i].strip(), vcode_list[i].strip(), f"Account#{i+1}"))

    if not accounts:
        raise ValueError("没有配置任何账户信息")

    success, fail = 0, 0
    for kps, sign, vcode, alias in accounts:
        ok, msg = sign_once(kps, sign, vcode, alias)
        if ok:
            success += 1
            print("✅", msg)
        else:
            fail += 1
            print("❌", msg)

    print(f"\n总结：{success} 成功，{fail} 失败，总共 {len(accounts)} 个账户")

if __name__ == "__main__":
    main()
