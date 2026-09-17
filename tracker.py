import os
import smtplib
from email.message import EmailMessage
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

URL = "https://www.costco.com/p/-/cuckoo-6-cup-twin-pressure-rice-cooker/4000180372"


def get_price():
  with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=True,
        args=[
            "--disable-http2",
            "--disable-blink-features=AutomationControlled",
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-dev-shm-usage",
        ],
    )

    context = browser.new_context(
        user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            " (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        ),
        viewport={"width": 1920, "height": 1080},
        locale="en-US",
    )

    page = context.new_page()

    # Native stealth evasion scripts:
    page.add_init_script("""
            // Overwrite the `languages` property to use standard English
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en']
            });
            // Overwrite the `plugins` property to simulate installed plugins
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
            // Pass the Chrome runtime test
            window.chrome = { runtime: {} };
            // Hide webdriver flag
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)

    print("Navigating to Costco URL...")
    page.goto(URL, wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(5000)

    html_content = page.content()
    browser.close()

  soup = BeautifulSoup(html_content, "html.parser")

  price_element = (
      soup.find("span", {"automation-id": "totalPriceOutput"})
      or soup.find("div", id="pull-right-price")
      or soup.select_one(".your-price .value")
      or soup.select_one(".price .value")
  )

  if price_element:
    return price_element.get_text(strip=True)

  if "Sign in to see price" in soup.get_text():
    return "Member-only price: Sign in required on Costco"

  if "Access Denied" in soup.get_text():
    return "Access Denied by Costco Akamai Shield"

  return "Price tag not found"


def send_email(price):
  sender_email = os.environ.get("SENDER_EMAIL")
  sender_password = os.environ.get("SENDER_PASSWORD")
  recipient_email = os.environ.get("RECIPIENT_EMAIL")

  msg = EmailMessage()
  msg["Subject"] = f"Costco Rice Cooker Daily Price: {price}"
  msg["From"] = sender_email
  msg["To"] = recipient_email
  msg.set_content(
      f"Item: Cuckoo 6-Cup Twin Pressure Rice Cooker\n"
      f"Current Price: {price}\n\n"
      f"View item: {URL}"
  )

  with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
    server.login(sender_email, sender_password)
    server.send_message(msg)
  print(f"Email successfully sent with price: {price}")


if __name__ == "__main__":
  current_price = get_price()
  print(f"Extracted Price: {current_price}")
  send_email(current_price)
