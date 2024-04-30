
import os
from robocorp.tasks import task
from robocorp import browser

from RPA.HTTP import HTTP
from RPA.PDF import PDF
from RPA.Tables import Tables
from RPA.Archive import Archive
page = browser.page()

@task
def order_robots_from_RobotSpareBin():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """
    browser.configure(
        slowmo = 2000
    )
    open_robot_order_website()
    download_orders_file()
    close_annoying_modal()
    orders = get_orders()
    for order in orders:
        fill_the_form(order)
        click_preview()
        screenshot_robot(order['Order number'])
        click_order()
        store_receipt_as_pdf(order['Order number'])
        embed_screenshot_to_receipt(order['Order number'])
        order_another()
        close_annoying_modal()

    archive_receipts()

def open_robot_order_website():
    browser.goto("https://robotsparebinindustries.com/#/robot-order")

def download_orders_file():
    http= HTTP()
    http.download("https://robotsparebinindustries.com/orders.csv",overwrite=True)

def get_orders():
    tables=Tables()
    table=tables.read_table_from_csv("orders.csv")
    return table

def close_annoying_modal():
     """to get rid of that annoying modal that 
     pops up when you open 
     the robot order website"""
     page.click('text=OK')

def fill_the_form(order):
    page.select_option("#head", str(order["Head"]))
    page.click(f"#id-body-{order['Body']}")
    page.fill('//input[@placeholder="Enter the part number for the legs"]', str(order["Legs"]))
    page.fill("#address", str(order["Address"]))

def click_preview():
    page.click("button:text('Preview')")

def screenshot_robot(order_number):
  out_path = f'output/screenshots/screenshot-{order_number}.png'
  image_loc = page.locator('//*[@id="robot-preview-image"]')
  image_loc.screenshot(path=out_path)
  return str(out_path)

def click_order():
    page.click("button:text('Order')")
    while page.locator("//div[@class='alert alert-danger']").is_visible():
        page.click("button:text('Order')")

def store_receipt_as_pdf(order_number):
    receipt = page.locator("#receipt").inner_html()

    pdf = PDF()
    receipt_pdf_path = f"output/receipts/receipt-{order_number}.pdf"
    pdf.html_to_pdf(receipt, receipt_pdf_path) 

def embed_screenshot_to_receipt(order_number):
     pdf=PDF()
     pdf.add_watermark_image_to_pdf(
        image_path=f"output/screenshots/screenshot-{order_number}.png",
        source_path=f"output/receipts/receipt-{order_number}.pdf",
        output_path=f"output/receipts/receipt-{order_number}.pdf",
    )       

def order_another():
   page.click("button:text('Order another robot')")

def archive_receipts():
    arch = Archive()
    arch.archive_folder_with_zip("output/receipts", "output/receipts.zip")   
