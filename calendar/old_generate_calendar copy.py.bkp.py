import csv
import calendar
import asyncio
from pathlib import Path
from pyppeteer import launch

# Mapping for tithi numbers
TITHI_MAPPING = {
    "Prathama": 1,
    "Dvitiiya": 2,
    "Tritiiya": 3,
    "Chaturthi": 4,
    "Panchami": 5,
    "Shashthi": 6,
    "Saptami": 7,
    "Ashtami": 8,
    "Navami": 9,
    "Dashami": 10,
    "Ekadashi": 11,
    "Dvadashi": 12,
    "Trayodashi": 13,
    "Chaturdashi": 14,
    "Purnima": 15,
    "Amavasya": 15
}

# Load CSV data
def load_csv(file_name):
    with open(file_name, newline='') as csvfile:
        return list(csv.DictReader(csvfile))

# Generate HTML calendar
# Generate HTML calendar
def generate_html_calendar(year, month, days_info, month_info):
    cal = calendar.HTMLCalendar(calendar.SUNDAY)
    month_calendar = cal.monthdayscalendar(year, month)

    # Check if the last row contains valid dates, indicating a fifth row
    if len(month_calendar) == 6:
        # If the first week is not empty, move the last row's days to the first row
        last_week = month_calendar[-1]
        first_week = month_calendar[0]

        for i in range(len(first_week)):
            if first_week[i] == 0 and last_week[i] > 0:  # Empty slot in the first week
                first_week[i] = last_week[i]  # Move the day from the last row to the first row
                last_week[i] = 0  # Clear the moved day

        # Remove the now-empty last week
        month_calendar.pop()

    # Find the relevant month info
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
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                table-layout: fixed;
            }}
            th {{
                background-color: #f2f2f2;
                padding: 10px;
            }}
            td {{
                padding: 10px;
                border: 1px solid #ddd;
                text-align: left;
                vertical-align: top;
                width: 14.28%;
                height: 150px;
                position: relative;
            }}
            .noday {{
                background-color: #f9f9f9;
            }}
            .header-img {{
                display: block;
                margin: 0 auto;
                height: auto;
                width: auto;
                max-width: 720px;
                max-height: 300px;
            }}
            h1 {{
                text-align: center;
                margin: 10px 10;
                font-size: 20px;
            }}
            h2 {{
                text-align: center;
                margin: 10px 10;
                font-size: 16px;
            }}
            .date {{
                font-weight: bold;
                color: blue;
                position: absolute;
                top: 5px;
                left: 5px;
            }}
            .nakshatra {{
                font-size: smaller;
                color: darkorange;
                text-align: center;
                position: absolute;
                top: 5px;
                left: 50%;
                transform: translateX(-50%);
            }}
            .tithi-paksha {{
                font-size: smaller;
                color: green;
                position: absolute;
                top: 5px;
                right: 5px;
            }}
            .events {{
                margin-top: 40px;
                font-size: smaller;
                line-height: 1.2;
            }}
            .temple-festivals {{
                background-color: #ffd700;
            }}
            .temple-monthly-poojas {{
                background-color: #fffacd;
            }}
            .balavihar-events {{
                background-color: #add8e6;
            }}
        </style>
    </head>
    <body>
        <img src="header.png" alt="Header Image" class="header-img">
        <h1>{calendar.month_name[month]} {year}</h1>
        <h2 style="text-align: center;">Lunar Month: {lunar_month} | Tamil Month: {tamil_month}</h2>
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
                    tithi = TITHI_MAPPING.get(day_info['tithi'], day_info['tithi'])
                    paksha = "P" if "Shukla" in day_info['paksha'] else "K"
                    nakshatra = day_info['nakshatra']
                    temple_festivals = day_info['temple_festivals']
                    temple_monthly_poojas = day_info['temple_monthly_poojas']
                    balavihar_events = day_info['balavihar_events']
                    festivals = day_info['festivals']

                    # Combine events with appropriate styles
                    events_html = ""
                    if temple_festivals:
                        events_html += f'<div class="temple-festivals">{temple_festivals}</div>'
                    if temple_monthly_poojas:
                        events_html += f'<div class="temple-monthly-poojas">{temple_monthly_poojas}</div>'
                    if balavihar_events:
                        events_html += f'<div class="balavihar-events">{balavihar_events}</div>'
                    if festivals:
                        events_html += f'<div>{festivals}</div>'

                    html_content += f"""
                    <td>
                        <div class="date">{day}</div>
                        <div class="nakshatra">{nakshatra}</div>
                        <div class="tithi-paksha">{tithi} {paksha}</div>
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


# Save HTML file
def save_html_file(content, month, year):
    file_name = f"calendar_{year}_{month}.html"
    with open(file_name, 'w') as file:
        file.write(content)
    print(f"Generated {file_name}")
    return file_name

async def generate_pdf(input_html, output_pdf):
    try:
        # Convert input HTML file path to an absolute path
        input_html_path = Path(input_html).resolve()

        browser = await launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])
        page = await browser.newPage()

        # Use the correct `file://` URL format
        await page.goto(f'file://{input_html_path}')
        await page.pdf({
            'path': output_pdf,
            'format': 'A4',
            'landscape': True,
            'scale': 0.7
            })

        await browser.close()
        print(f"PDF generated: {output_pdf}")
    except Exception as e:
        print(f"Error generating PDF: {e}")

# Main function
def main():
    days_info = load_csv('days.csv')
    month_info = load_csv('months.csv')

    year = 2025

    for month in range(8, 9):  # Update range as needed
        html_calendar = generate_html_calendar(year, month, days_info, month_info)
        html_file = save_html_file(html_calendar, month, year)

        # Generate PDF
        pdf_file = f"calendar_{year}_{month}.pdf"
        asyncio.run(generate_pdf(html_file, pdf_file))
        print(f"Generated {pdf_file}")

if __name__ == "__main__":
    main()
