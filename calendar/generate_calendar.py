import csv
import calendar
import asyncio
import os
from pathlib import Path
from pyppeteer import launch
from PyPDF2 import PdfMerger

# Load CSV data
def load_csv(file_name):
    with open(file_name, newline='') as csvfile:
        return list(csv.DictReader(csvfile))

def generate_html_calendar(year, month, days_info, month_info):
    cal = calendar.HTMLCalendar(calendar.SUNDAY)
    month_calendar = cal.monthdayscalendar(year, month)

    # Adjust for six-row calendars
    if len(month_calendar) == 6:
        last_week = month_calendar[-1]
        first_week = month_calendar[0]

        for i in range(len(first_week)):
            if first_week[i] == 0 and last_week[i] > 0:
                first_week[i] = last_week[i]
                last_week[i] = 0

        month_calendar.pop()

    # Get the relevant month info
    month_data = next(item for item in month_info if int(item['month_index']) == month)
    lunar_month = month_data['lunar_month']
    tamil_month = month_data['tamil_month']

    # Start HTML content
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{calendar.month_name[month]} {year}</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 0;
                background-color: white;
            }}
            .header {{
                display: flex;
                align-items: center;
                padding: 10px 20px;
                border-bottom: 1px solid #ddd;
            }}
            .header-left {{
                flex: 1;
                text-align: left;
            }}
            .header-center {{
                flex: 1;
                display: flex;
                justify-content: center;
                text-align: center;
            }}
            .header-right {{
                flex: 1;
                text-align: right;
            }}
            .header img {{
                max-height: 130px;
                max-width: 100%;
            }}
            .header-text h1 {{
                margin: 0;
                font-size: 40px;
                font-weight: bold;
            }}
            .header-text h2 {{
                margin: 5px 0;
                font-size: 20px;
                font-weight: normal;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                table-layout: fixed;
            }}
            th {{
                background-color: #f2f2f2;
                padding: 10px;
                border: 2px solid #000;
            }}
            td {{
                padding: 10px;
                border: 2px solid #000;
                text-align: left;
                vertical-align: top;
                width: 14.28%;
                height: 150px;
                position: relative;
            }}
            .noday {{
                background-color: #f9f9f9;
            }}
            .date {{
                font-size: 28px;
                font-weight: bold;
                color: black;
                position: absolute;
                top: 5px;
                left: 5px;
            }}
            .tithi {{
                font-size: small;
                color: black;
                position: absolute;
                top: 5px;
                right: 5px;
            }}
            .nakshatra {{
                font-size: small;
                color: black;
                position: absolute;
                top: 25px;
                right: 5px;
            }}
            .paksha {{
                font-size: small;
                color: black;
                position: absolute;
                top: 45px;
                right: 5px;
            }}
            .events {{
                margin-top: 60px;
                font-size: smaller;
                line-height: 1.2;
            }}
            .events div {{
                margin-bottom: 5px;
            }}
            .temple-festivals {{
                background-color: #ffd700 !important;
                padding: 2px;
            }}
            .temple-monthly-poojas {{
                background-color: #fffacd !important;
                padding: 2px;
            }}
            .balavihar-events {{
                background-color: #add8e6 !important;
                padding: 2px;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <div class="header-left">
                <img src="../TextHeader.png" alt="Text Header">
            </div>
            <div class="header-center">
                <img src="../LogoHeader.png" alt="Logo Header">
            </div>
            <div class="header-right">
                <div class="header-text">
                    <h1>{calendar.month_name[month]} {year}</h1>
                    <h2>Lunar Month: {lunar_month}</h2>
                    <h2>Tamil Month: {tamil_month}</h2>
                </div>
            </div>
        </div>
        <table>
            <tr>
                {''.join(f'<th>{day}</th>' for day in ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"])}
            </tr>
    """

    for week in month_calendar:
        html_content += "<tr>"
        for day in week:
            if day == 0:
                html_content += '<td class="noday"></td>'
            else:
                date_str = f"{month}/{day}/{year}"
                day_info = next((item for item in days_info if item['date'] == date_str), None)
                if day_info:
                    tithi = day_info['tithi']
                    paksha = "○" if "Shukla" in day_info['paksha'] else "●"
                    nakshatra = day_info['nakshatra']
                    temple_festivals = day_info['temple_festivals']
                    temple_monthly_poojas = day_info['temple_monthly_poojas']
                    balavihar_events = day_info['balavihar_events']
                    festivals = day_info['festivals']

                    events_html = ""
                    if balavihar_events:
                        events_html += f'<div class="balavihar-events">{balavihar_events}</div>'
                    if temple_festivals:
                        events_html += f'<div class="temple-festivals">{temple_festivals}</div>'
                    if temple_monthly_poojas:
                        events_html += f'<div class="temple-monthly-poojas">{temple_monthly_poojas}</div>'
                    if festivals:
                        events_html += f'<div>{festivals}</div>'

                    html_content += f"""
                    <td>
                        <div class="date">{day}</div>
                        <div class="tithi">T: {tithi}</div>
                        <div class="nakshatra">N: {nakshatra}</div>
                        <div class="paksha">{paksha}</div>
                        <div class="events">
                            {events_html}
                        </div>
                    </td>
                    """
                else:
                    html_content += f"<td><div class='date'>{day}</div></td>"
        html_content += "</tr>"

    html_content += """
        </table>
    </body>
    </html>
    """
    return html_content

# async def generate_pdf(input_html, output_pdf):
#     try:
#         # Convert input HTML file path to an absolute path
#         input_html_path = Path(input_html).resolve()

#         browser = await launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])
#         page = await browser.newPage()

#         # Use the correct `file://` URL format
#         await page.goto(f'file://{input_html_path}')
#         await page.pdf({
#             'path': output_pdf,
#             'format': 'A4',
#             'landscape': True,
#             'scale': 0.65,
#             'margin': {
#                 'top': '10mm',
#                 'bottom': '10mm',
#                 'left': '10mm',
#                 'right': '10mm'
#             }
#             })

#         await browser.close()
#         print(f"PDF generated: {output_pdf}")
#     except Exception as e:
#         print(f"Error generating PDF: {e}")

async def generate_pdf(input_html, output_pdf):
    try:
        # Convert input HTML file path to an absolute path
        input_html_path = Path(input_html).resolve()

        browser = await launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])
        page = await browser.newPage()

        # Use the correct `file://` URL format
        await page.goto(f'file://{input_html_path}', waitUntil='networkidle0')  # Wait until network is idle

        # Adding a small sleep to ensure that the page is fully rendered
        await asyncio.sleep(1)  # Sleep for 1 second to ensure page is rendered

        # Generate PDF with the desired settings
        await page.pdf({
            'path': output_pdf,
            'format': 'A4',
            'landscape': True,
            'scale': 0.65,
            'printBackground': True,
            'margin': {
                'top': '10mm',
                'bottom': '10mm',
                'left': '10mm',
                'right': '10mm'
            }
        })

        await browser.close()
        print(f"PDF generated: {output_pdf}")
    except Exception as e:
        print(f"Error generating PDF: {e}")

def merge_pdfs(pdf_files, output_file):
    """Merge multiple PDF files into a single PDF."""
    merger = PdfMerger()
    try:
        for pdf in pdf_files:
            merger.append(str(pdf))
        merger.write(output_file)
        print(f"Merged PDF created: {output_file}")
    except Exception as e:
        print(f"Error merging PDFs: {e}")
    finally:
        merger.close()

def save_html_file(content, file_path):
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with open(file_path, 'w') as file:
        file.write(content)
    print(f"Generated {file_path}")
    return str(file_path)


def main():
    days_info = load_csv('days.csv')
    month_info = load_csv('months.csv')

    year = 2025
    start_month, end_month = 1, 12

    html_folder = Path("generated_htmls")
    pdf_folder = Path("generated_pdfs")
    html_folder.mkdir(exist_ok=True)
    pdf_folder.mkdir(exist_ok=True)

    pdf_files = []

    for month in range(start_month, end_month + 1):
        html_calendar = generate_html_calendar(year, month, days_info, month_info)

        html_file = html_folder / f"calendar_{year}_{month}.html"
        save_html_file(html_calendar, html_file)
        print(f"Generated HTML: {html_file}")

        pdf_file = pdf_folder / f"calendar_{year}_{month}.pdf"
        asyncio.run(generate_pdf(html_file, pdf_file))
        print(f"Generated PDF: {pdf_file}")

        pdf_files.append(pdf_file)

    merged_pdf_file = pdf_folder / f"calendar_{year}_merged.pdf"
    merge_pdfs(pdf_files, merged_pdf_file)
    print(f"Generated merged PDF: {merged_pdf_file}")

if __name__ == "__main__":
    main()
