import calendar
import random
import subprocess
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, letter, inch, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from random import choice
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer, Paragraph, PageTemplate, BaseDocTemplate, \
    Frame
from flask import Flask, request, send_from_directory
import os
from flask_cors import CORS
from data import breakfast_drink, breakfast, lunch, dinner

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


class CalendarPageTemplate(PageTemplate):
    def __init__(self):
        frames = [
            Frame(
                x1=72, y1=72, width=letter[0] - 144, height=letter[1] - 144,
                leftPadding=0, rightPadding=0, bottomPadding=0, topPadding=0,
                id='normal'
            )
        ]
        super().__init__('CalendarPageTemplate', frames=frames)

    def afterDrawPage(self, canvas, doc):
        month = doc.month
        year = doc.year
        month_name = calendar.month_name[month]
        substitutions = "Substitutions: Leftovers, sandwich, soup, veggies, fruit, cottage cheese"
        snacks = "Snacks: crackers, chips, pastries, pudding, fruit, yogurt, apple sauce, ice-cream"
        canvas.setFont('Helvetica-Bold', 24)
        canvas.drawCentredString(letter[0] / 2, letter[1] - 50, f'{month_name} Menu {year}')
        canvas.setFont('Helvetica', 16)
        footer_x = 275
        footer_y_substitutions = 55
        footer_y_snacks = footer_y_substitutions - 25
        # Draw the substitutions line
        canvas.drawCentredString(footer_x, footer_y_substitutions, substitutions)
        # Draw the snacks line
        canvas.drawCentredString(footer_x + 30, footer_y_snacks, snacks)

# Menu Endpoint
@app.route('/generate-menu', methods=['POST'])
def generate_menu():
    month = int(request.form.get('month'))
    year = int(request.form.get('year'))

    file_name = create_menu(year, month)

    # Serve the PDF back to the client
    return send_from_directory('.', file_name, as_attachment=True, mimetype='application/pdf')


# Activity Endpoint
@app.route('/generate-calendar', methods=['POST'])
def generate_calendar():
    month = int(request.form.get('month'))
    year = int(request.form.get('year'))

    file_name = create_calendar(year, month)
   
    directory, file_name = os.path.split(file_name)
    return send_from_directory(directory, file_name, as_attachment=True, mimetype='application/pdf')


# Activity Generator Function
def create_calendar(year, month):
    activity_list = ["Movies", "Walk", "Exercise", "Bird Watching", "Puzzles", "Trivia", "Baking",
              "Gardening", "Stretching", "Family Calls", "ROM Exercise", "Coloring", "Arts & Crafts", "Bingo",
              "Card Games", "Music", "Board Games", "Dominoes", "Balloon Volleyball", "Tea Time Social", "Arts and Music", "Chair Zumba", "Virtual Museum Tours", "Indoor Bowling",
              "Puzzle Quilts", "Ice-Cream Social", "Indoor Minigolf", "Brain Teasers", "Group Meditation", "DIY Craft Projects", "Group Painting", "Storytelling Circle"]
   
    file_name = "Activity-Calendar-{}-{}.pdf".format(calendar.month_name[month], year)
    doc = SimpleDocTemplate("Activity-Calendar-{}-{}.pdf".format(calendar.month_name[month], year), pagesize=landscape(letter), topMargin=0.1*inch)
    activities_per_day = 3
    cal = calendar.monthcalendar(year, month)
    table_data = []
    headers = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    table_data.append(headers)
    for week in cal:
        week_data = []
        for day in week:
            if day == 0:
                week_data.append(" ")
            else:
                day_activities = []
                day_activities.append("Current Events")
                for i in range(activities_per_day - 1):
                    activity = choice(activity_list)
                    while activity in day_activities:
                        activity = choice(activity_list)
                    day_activities.append(activity)
                week_data.append("{}:\n - {}\n - {}".format(day, day_activities[0], "\n - ".join(day_activities[1:])))
        table_data.append(week_data)

    col_widths = [1.51*inch] * 7
    row_heights = [1.07*inch] * len(table_data)
   
    table = Table(table_data, colWidths=col_widths, rowHeights=row_heights)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))

    title_style = ParagraphStyle(
        name='Calendar Title',
        fontSize=30,
        alignment=TA_CENTER,
        spaceAfter=10,
        spaceBefore=0
    )

    title = Paragraph(f"<font size=30><b>{calendar.month_name[month]} Activities {year}</b></font>", style=title_style)

    doc.build([Spacer(1, 0.0003*inch), title, Spacer(1, 0.5*inch), table])  # Adjust spacer heights as needed

    return file_name


# Menu Generator Function
def create_menu(year, month):
    # Define the file name
    file_name = f"Menu-Calendar-{calendar.month_name[month]}-{year}.pdf"

    # Create a PDF document
    doc = SimpleDocTemplate(file_name, pagesize=letter)
    doc.month = month
    doc.year = year

    # Assign the custom PageTemplate to the document
    doc.addPageTemplates(CalendarPageTemplate())

    def meal(sequence):
        choice = random.choice(sequence)
        meal_text = ""
        for element in choice:
            meal_text += element + "\n"
        return meal_text

    # Get the calendar data for the current month
    cal = calendar.monthcalendar(year, month)

    # Define table data
    table_data = []
    headers = ['Day', 'Breakfast', 'Lunch', 'Dinner']
    table_data.append(headers)

    # Define past meals lists for breakfast. lunch, and dinner
    past_breakfast_meals = []
    past_lunch_meals = []
    past_dinner_meals = []

    for week in cal:
        for day in week:
            if day == 0:
                continue
            else:
                day_of_week = calendar.day_abbr[calendar.weekday(year, month, day)]

                # Generate unique meals for each day's breakfast, lunch, and dinner
                breakfast_choice = meal(breakfast)
                while breakfast_choice in past_breakfast_meals:
                    breakfast_choice = meal(breakfast)
                past_breakfast_meals.append(breakfast_choice)

                lunch_choice = meal(lunch)
                while lunch_choice in past_lunch_meals:
                    lunch_choice = meal(lunch)
                past_lunch_meals.append(lunch_choice)

                dinner_choice = meal(dinner)
                while dinner_choice in past_dinner_meals:
                    dinner_choice = meal(dinner)
                past_dinner_meals.append(dinner_choice)

                table_data.append([f"{day_of_week} ({day})", breakfast_choice, lunch_choice, dinner_choice])

                # Limit the size of past_meals lists to 7 days
                if len(past_breakfast_meals) > 7:
                    past_breakfast_meals.pop(0)
                if len(past_lunch_meals) > 7:
                    past_lunch_meals.pop(0)
                if len(past_dinner_meals) > 7:
                    past_dinner_meals.pop(0)

    # Create a table and add data
    table = Table(table_data, repeatRows=1)

    # Define table style
    table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),  # Header row background color
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),  # Header row text color
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Center alignment for all cells
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Header row font
        ('FONTSIZE', (0, 0), (-1, 0), 12),  # Header row font size
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),  # Header row bottom padding
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),  # Data rows background color
        ('GRID', (0, 0), (-1, -1), 1, colors.black),  # Gridlines
    ])

    # Apply table style
    table.setStyle(table_style)

    # Build the PDF document with the table
    elements = [Spacer(1, 12), table]  # Add the month name and some space before the table
    doc.build(elements)

    return file_name

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Use Heroku's port if available, otherwise default to 5000
    app.run(host='0.0.0.0', port=port)

