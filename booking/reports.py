from openpyxl import Workbook
import os
from .models import RoomType

def reports():
    # Your database query to retrieve data
    data = RoomType.objects.all()

    # Create a new workbook and add a worksheet
    wb = Workbook()
    ws = wb.active

    # Write headers
    headers = []
    for attr, value in vars(RoomType).items():
        headers.append(str(attr))

    ws.append(headers)  # Add your column names

    # Write data rows
    row = []
    for item in data:
        for attr, value in vars(item).items():
            row.append(item.attr)
        ws.append([row])  # Add your fields
        row = []

    # Get the current directory
    current_directory = os.getcwd()
    
    # Save the workbook
    file_name = 'my_data.xlsx'  # Change this to your desired file name
    file_path = os.path.join(current_directory, file_name)
    wb.save(file_path)

reports()