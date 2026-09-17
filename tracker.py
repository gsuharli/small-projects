import os
import smtplib
from email.message import EmailMessage
import requests
from bs4 import BeautifulSoup

# Target product URL
URL = "https://www.costco.com/p/-/cuckoo-6-cup-twin-pressure-rice-cooker/4000180372"

# Browser header to prevent bot blocks
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        " (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "DNT": "1",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "sec-ch-ua": (
        '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"'
    ),
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
}


def get_price():
  response = requests.get(session = requests.Session()
session.headers.update(HEADERS)
response = session.get(URL, timeout=15))
  response.raise_for_status()

  soup = BeautifulSoup(response.text, "html.parser")

  # Replace with your item's specific tag and class or ID:
  # Inspect the price element in your browser to find its selector.
  price_element = soup.find("span", class_="MuiTypography-root MuiTypography-bodyCopy mui-cqdqae") or soup.find(
      id="Text_single-price-whole-value"
  )

  if price_element:
    return price_element.get_text(strip=True)
  return "Price tag not found"


def send_email(price):
  sender_email = os.environ.get("SENDER_EMAIL")
  sender_password = os.environ.get("SENDER_PASSWORD")
  recipient_email = os.environ.get("RECIPIENT_EMAIL")

  msg = EmailMessage()
  msg["Subject"] = f"Daily Price Update: {price}"
  msg["From"] = sender_email
  msg["To"] = recipient_email
  msg.set_content(
      f"Current tracked price: {price}\n\nCheck the product here: {URL}"
  )

  with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
    server.login(sender_email, sender_password)
    server.send_message(msg)


if __name__ == "__main__":
  current_price = get_price()
  send_email(current_price)
