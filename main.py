import yfinance as yf
import pandas as pd
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
import os

curr_dir = os.getcwd()
EXCEL_FILE = os.path.join(curr_dir, 'sbi_friday_closing_prices.xlsx')

def fetch_friday_closing_price():
    ticker_symbol = 'SBIN.BO'
    sbi_data = yf.Ticker(ticker_symbol)
    hist = sbi_data.history(period='5d')
    fridays = hist[hist.index.weekday == 4]

    if not fridays.empty:
        friday_date = fridays.index[0].date()
        friday_close = fridays['Close'].iloc[0]
        today = datetime.now().date()

        # Check if the Excel file exists and read the data
        if os.path.exists(EXCEL_FILE):
            df = pd.read_excel(EXCEL_FILE)
        else:
            df = pd.DataFrame(columns=['Date', 'Close'])
        print(df.columns)
        # Convert 'Date' column to datetime to avoid issues with date comparison
        df['Date'] = pd.to_datetime(df['Date']).dt.date

        # Check if today's date is already in the data
        if friday_date in df['Date'].values:
            print(f"Data for {friday_date} is already present. Skipping appending.")
        else:
            new_row = pd.DataFrame({'Date': [friday_date], 'Close': [friday_close]})
            df = pd.concat([df, new_row], ignore_index=True)
            df.to_excel(EXCEL_FILE, index=False)
            print(f"Appended data: {friday_date} - {friday_close}")
            send_email(EXCEL_FILE)
    else:
        print(f"No trading data available for today, {friday_date}")

def send_email(file_path):
    sender_email = os.getenv('SENDER_EMAIL')
    receiver_email = os.getenv('RECEIVER_EMAIL')
    password = os.getenv('EMAIL_PASSWORD')
    subject = 'SBI Friday Closing Prices'
    body = 'Please find attached the latest SBI Friday closing prices.'

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    attachment = MIMEBase('application', 'octet-stream')
    with open(file_path, 'rb') as attachment_file:
        attachment.set_payload(attachment_file.read())
    encoders.encode_base64(attachment)
    attachment.add_header('Content-Disposition', f'attachment; filename={os.path.basename(file_path)}')
    msg.attach(attachment)

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)  # Use Gmail's SMTP server
        server.starttls()
        server.login(sender_email, password)
        text = msg.as_string()
        server.sendmail(sender_email, receiver_email, text)
        server.quit()
        print('Email sent successfully!')
    except Exception as e:
        print(f'Failed to send email: {e}')

fetch_friday_closing_price()
print("Task is done.")

