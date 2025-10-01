import os
import json
import requests
import traceback


def load_accounts():
    """解析账户信息，优先使用 QUARK_ACCOUNTS (JSON 数组)，否则使用三件套。"""
    acc_env = os.getenv("QUARK_ACCOUNTS", "").strip()
    accounts = []

    if acc_env:
        try:
            # JSON 数组格式
            if acc_env.startswith('['):
                arr = json.loads(acc_env)
                for i, it in enumerate(arr, 1):
                    kps = it.get("kps", "").strip()
                    sign = it.get("sign", "").strip()
                    vcode = it.get("vcode", "").strip()
                    alias = it.get("alias", f"Account#{i}")
                    if not (kps and sign and vcode):
                        raise ValueError(f"JSON 第 {i} 个对象缺少 kps/sign/vcode")
                    accounts.append((kps, sign, vcode, alias))
                return accounts
        except json.JSONDecodeError:
            raise ValueError("QUARK_ACCOUNTS 不是合法的 JSON，请检查格式")

    # 如果 JSON 没有提供，则使用三件套
    kps_list = [x.strip() for x in os.getenv("QUARK_KPS", "").split(",") if x.strip()]
    sign_list = [x.strip() for x in os.getenv("QUARK_SIGN", "").split(",") if x.strip()]
    vcode_list = [x.strip() for x in os.getenv("QUARK_VCODE", "").split(",") if x.strip()]

    if kps_list and (len(kps_list) == len(sign_list) == len(vcode_list)):
        for i in range(len(kps_list)):
            accounts.append((kps_list[i], sign_list[i], vcode_list[i], f"Account#{i+1}"))

    if not accounts:
        raise ValueError("未找到任何账户，请配置 QUARK_ACCOUNTS (JSON) 或三件套 Secrets")

    return accounts


def sign_once(kps, sign, vcode, alias):
    """单个账号签到"""
    try:
        headers = {
            "Cookie": f"QUARK_KPS={kps}; QUARK_SIGN={sign}; QUARK_VCODE={vcode}",
            "User-Agent": "okhttp/3.12.12"
        }
        url = "https://drive-m.quark.cn/1/clouddrive/capacity/growth/sign_in"
        resp = requests.post(url, headers=headers, timeout=15)
        data = resp.json()
        if data.get("code") == 0:
            reward = data.get("data", {}).get("capacity", "未知")
            return True, f"{alias} 签到成功，获得 {reward} 容量"
        else:
            return False, f"{alias} 签到失败：{data}"
    except Exception as e:
        return False, f"{alias} 异常：{e}\n{traceback.format_exc()}"


def main():
    accounts = load_accounts()
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
