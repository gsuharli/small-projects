import os
import smtplib
from email.message import EmailMessage
import requests
from bs4 import BeautifulSoup

# Target product URL
URL = "https://example.com/product-page"

# Browser header to prevent bot blocks
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


def get_price():
  response = requests.get(URL, headers=HEADERS, timeout=15)
  response.raise_for_status()

  soup = BeautifulSoup(response.text, "html.parser")

  # Replace with your item's specific tag and class or ID:
  # Inspect the price element in your browser to find its selector.
  price_element = soup.find("span", class_="a-price-whole") or soup.find(
      id="priceblock_ourprice"
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
