from robocorp.tasks import task
from robocorp import browser
from RPA.HTTP import HTTP
from RPA.Excel.Files import Files
from RPA.Tables import Tables
from RPA.Archive import Archive
import shutil



from RPA.PDF import PDF

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
        screenshot="only-on-failure",
        slowmo= 100,
    )
    open_robot_order_website()
    download_orders()
    fill_form_with_csv_data()
    # Handle pop-up alert
    fill_form_with_csv_data()
    archive_receipts()
    # clean_up()
    




def open_robot_order_website():
    """ Opens the website from where we need to order the robots."""
    browser.goto("https://robotsparebinindustries.com/#/robot-order")
    page = browser.page()
    page.click('text =OK')

def download_orders():
    """ Downloads the orders and creates a ZIP archive."""
    http = HTTP()
    http.download(url = "https://robotsparebinindustries.com/orders.csv", 
                  target_file='output/orders.csv',
                  overwrite=True)

def fill_form_with_csv_data():
    """Read data from csv and fill in the robot order form"""
    csv_file = Tables()
    robot_orders = csv_file.read_table_from_csv("output/orders.csv")
    for order in robot_orders:
        submit_order(order)
  

def order_another_bot():
    """Clicks on order another button to order another bot"""
    page = browser.page()
    page.click("#order-another")
    clicks_ok()

def clicks_ok():
    """Clicks on ok whenever a new order is made for bots"""
    try:
        page = browser.page()
        page.wait_for_selector("text=OK", timeout=5000)  # Wait for pop-up
        page.click("text=OK")  # Click "OK" button
        print("Pop-up handled successfully.")
    except Exception as e:
        print(f"No pop-up found or error occurred: {e}")


def submit_order(order):
    """ Submits the order."""
    page = browser.page()
    page.select_option("#head", str(order["Head"]))
    
    # Select the Body radio button
    body_value = str(order["Body"])
    page.click(f'input[name="body"][value="{body_value}"]')  # Correct way to select radio button
    # Fill Legs input field (Verify the correct selector in the webpage)
    page.fill('input[placeholder="Enter the part number for the legs"]', str(order["Legs"])) # Assuming "1740219912921" is the correct ID

    page.fill("#address", order["Address"])

    while True:
        page.click("#order")
        order_another = page.query_selector("#order-another")
        if order_another:
            pdf_path = store_receipt_as_pdf(int(order["Order number"]))
            screenshot_path = screenshot_robot(int(order["Order number"]))
            embed_screenshot_to_receipt(screenshot_path, pdf_path)
            order_another_bot()
            clicks_ok()
            break

    
def store_receipt_as_pdf(order_number):
    """ Stores the order receipt as a PDF file."""
    page = browser.page()
    order_receipt_html = page.locator("#receipt").inner_html()

    pdf = PDF()
    pdf_path = "output/receipts/{0}.pdf".format(order_number)
    pdf.html_to_pdf(order_receipt_html, pdf_path)
    return pdf_path



def screenshot_robot(order_number):
    """ Takes a screenshot of the ordered robot."""
    page = browser.page()
    screenshot_path = "output/receipts-screenshot/{0}.png".format(order_number)
    page.locator("#robot-preview-image").screenshot(path=screenshot_path)
    return screenshot_path

def embed_screenshot_to_receipt(screenshot_path, pdf_path):
    """ Embeds the screenshot of the robot to the PDF receipt."""
    pdf = PDF()
    pdf.add_watermark_image_to_pdf(image_path=screenshot_path, 
                                   source_path=pdf_path, 
                                   output_path=pdf_path)


def archive_receipts():
    """Archives all the receipt pdfs into a single zip archive"""
    lib = Archive()
    lib.archive_folder_with_zip("./output/receipts", "./output/receipts.zip")

# def clean_up():
#     """Cleans up the folders where receipts and screenshots are saved."""
#     shutil.rmtree("./output/receipts")
#     shutil.rmtree("./output/receipt-screenshots")





    