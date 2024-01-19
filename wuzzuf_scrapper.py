import tkinter as tk
from tkinter import ttk, scrolledtext
import webbrowser
import requests
from bs4 import BeautifulSoup
import csv
import time

class JobScraper:
    def __init__(self, job_title, num_pages):
        self.job_title = job_title
        self.num_pages = num_pages
        self.file_name = f'{job_title.title()} Jobs.csv'
        self.base_url = 'https://wuzzuf.net'
        self.counter = 1  # Initialize the counter

    def scrape_jobs(self, display_mode, tree, text_widget, completion_text):
        # open csv file and write header
        with open(self.file_name, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Num', 'JobTitle', 'Company', 'Location', 'Time',
                             'Job URL', 'Job Type', 'Experience', 'Job Categories', 'Job Skills'])

            # scrape jobs from each page
            for i in range(self.num_pages + 1):
                url = f'https://wuzzuf.net/search/jobs/?a=hpb%7Cspbg&q={self.job_title}&start={i}'
                page = requests.get(url, headers={"Accept-Encoding": "utf-8"})

                soup = BeautifulSoup(page.content, 'html.parser')
                jobs = soup.find_all('div', class_="css-1gatmva e1v1l3u10")

                if len(jobs) == 0:
                    break

                for job in jobs:
                    # get job information
                    job_title = job.find('h2', class_="css-m604qf").text.strip().replace(', ', '-')
                    company_elem = job.find('a', class_="css-17s97q8").text.strip().split()
                    company = ' '.join(company_elem[:-1])
                    location = job.find('span', class_="css-5wys0k").text.strip().replace(', ', '-')
                    time_posted_elem = job.find('div', class_="css-4c4ojb")
                    time_posted = time_posted_elem.text.strip() if time_posted_elem else ''
                    job_url = job.find('a', class_="css-o171kl")['href']

                    job_type_elem = job.find_all('a', class_="css-n2jc4m")
                    job_type = ' | '.join(job_type.text.strip() for job_type in job_type_elem)

                    # Extracting job details
                    details = job.find('div', class_="css-y4udm8")
                    categories = details.find_all('a', class_="css-o171kl")
                    skills = details.find_all('a', class_="css-5x9pm1")

                    experience_elem = categories[0].text.strip()
                    experience_span = details.find_all('span')
                    experience = f'{experience_elem} | {experience_span[1].text[2:].strip()}' if (
                            (len(experience_span) > 1) and 'Yrs' in experience_span[1].text.strip()) else experience_elem

                    job_categories = ' | '.join([category.text[2:].strip() for category in categories[1:]])

                    # Handling skills
                    job_skills = []
                    for skill in skills:
                        if skill.find('span'):
                            # If the skill has a span, extract the text from the span
                            job_skills.append(skill.find('span').text.strip())
                        else:
                            # If there is no span, directly extract the text
                            job_skills.append(skill.text[2:].strip())

                    job_skills_str = ' | '.join(job_skills)

                    if display_mode == 'Treeview':
                        # Insert job information into the Treeview
                        tree.insert('', 'end', values=[self.counter, job_title, company, location, time_posted,
                                                       job_type, experience, job_categories, job_skills_str, job_url])
                        # Hide the ScrolledText widget
                        text_widget.pack_forget()

                    elif display_mode == 'ScrolledText':
                        # Insert job information into the ScrolledText
                        text_widget.insert(tk.END, f'{self.counter})\n'
                                                   f'Job Title: {job_title}\n'
                                                   f'Company: {company}\n'
                                                   f'Location: {location}\n'
                                                   f'Time Posted: {time_posted}\n'
                                                   f'Job URL: ')

                        # Make the URL clickable
                        text_widget.tag_config(f'url_{self.counter}', foreground='blue', underline=True)
                        text_widget.insert(tk.END, job_url, f'url_{self.counter}')
                        text_widget.insert(tk.END, f'\nJob Type: {job_type}\n'
                                                   f'Experience: {experience}\n'
                                                   f'Job Categories: {job_categories}\n'
                                                   f'Job Skills: {job_skills_str}\n'
                                                   f'{"-" * 100}\n{"-" * 100}\n')

                        # Add binding to open URL on click
                        text_widget.tag_bind(f'url_{self.counter}', '<Button-1>',
                                             lambda event, url=job_url: webbrowser.open_new(url))
                        # Hide the Treeview widget
                        tree.pack_forget()
                        x_scrollbar.pack_forget()

                    # Write job information to csv file
                    writer.writerow([self.counter, job_title, company, location, time_posted, job_type,
                                     experience, job_categories, job_skills_str, job_url])

                    # Update the display
                    window.update()

                    self.counter += 1  # Increment the counter

                # add a delay between requests to prevent getting blocked
                time.sleep(2)

        print(f'Scraping for "{self.job_title}" jobs is complete. Data has been written to "{self.file_name}".')
        completion_text.set(
            f'Scraping for "{self.job_title}" jobs is complete. {self.counter - 1} records have been inserted to "{self.file_name}".')

def scrape_jobs_gui():
    job_title = job_title_entry.get()
    num_pages = int(num_pages_entry.get())
    display_mode = mode_combobox.get()

    # Clear previous data
    tree.delete(*tree.get_children())
    text_widget.delete('1.0', tk.END)

    # Show the appropriate widget based on the selected mode
    if display_mode == 'Treeview':
        tree.pack()
        x_scrollbar.pack(fill='x')
    elif display_mode == 'ScrolledText':
        text_widget.pack()

    job_scraper = JobScraper(job_title, num_pages)
    job_scraper.scrape_jobs(display_mode, tree, text_widget, completion_text)

# Create the main window
window = tk.Tk()
window.title('Job Scraper')
window.configure(bg='black')
window.state('zoomed')

# Create a style for the Treeview
style = ttk.Style()
style.configure("Treeview.Heading", font=('Arial', 14, 'bold'), foreground='red')
style.configure("Treeview", font=('Arial', 12))

# Create a label for the title
title_label = tk.Label(window, text='Scrapping WUZZUF Jobs', font=('Arial', 20, 'bold'), fg='white', bg='black')
title_label.pack(pady=10)

# Create a label and entry for job title input
job_title_label = tk.Label(window, text='Job Title', font=('Arial', 16, 'bold'), fg='white', bg='black')
job_title_label.pack()

job_title_entry = tk.Entry(window, justify='center', font=('Arial', 14))
job_title_entry.pack(pady=5)

num_pages_label = tk.Label(window, text='No.of of Pages', font=('Arial', 16, 'bold'), fg='white', bg='black')
num_pages_label.pack()

num_pages_entry = tk.Entry(window, justify='center', font=('Arial', 14))
num_pages_entry.pack(pady=5)

# Create a Combobox for display mode
mode_label = tk.Label(window, text='Display Mode', font=('Arial', 16, 'bold'), fg='white', bg='black')
mode_label.pack()

mode_combobox = ttk.Combobox(window, values=['Treeview', 'ScrolledText'], font=('Arial', 14))
mode_combobox.pack(pady=5)
mode_combobox.set('Treeview')  # Default mode

button = tk.Button(window, text='Scrape Jobs', command=scrape_jobs_gui, font=('Arial', 14), bg='white', fg='red')
button.pack(pady=10)

# Create a Treeview widget to display the results in columns
tree = ttk.Treeview(window, columns=['ID', 'Job Title', 'Company', 'Location', 'Time Posted',
                                     'Job Type', 'Experience', 'Job Categories', 'Job Skills', 'Job URL'],
                    show='headings', height=15)
tree.pack()

# Create a horizontal scrollbar
x_scrollbar = ttk.Scrollbar(window, orient='horizontal', command=tree.xview)
x_scrollbar.pack(fill='x')

# Set column headings and widths
columns_and_widths = {'ID': 60, 'Job Title': 350, 'Company': 200, 'Location': 150, 'Time Posted': 150,
                      'Job Type': 150, 'Experience': 150, 'Job Categories': 200, 'Job Skills': 300, 'Job URL': 250}

for col, width in columns_and_widths.items():
    tree.heading(col, text=col, anchor='center')
    tree.column(col, width=width, anchor='center')

# Create a ScrolledText widget to display the results
text_widget = scrolledtext.ScrolledText(window, wrap=tk.WORD, width=150, height=20, font=('Arial', 12))
text_widget.pack(padx=10, pady=10)

# Initially hide Treeview, x_scrollbar, and ScrolledText widgets
tree.pack_forget()
x_scrollbar.pack_forget()
text_widget.pack_forget()

# Create a label for the completion message
completion_text = tk.StringVar()
completion_label = tk.Label(window, textvariable=completion_text, font=('Arial', 14, 'bold'), fg='white', bg='black')
completion_label.pack(pady=10)

# Create a label for the watermark
watermark_label = tk.Label(window, text='Made by: Abdelrahman Eldaba', font=('Arial', 12), fg='white', bg='black')
watermark_label.place(relx=0.5, rely=0.95, anchor='center')

# Start the GUI event loop
window.mainloop()

# Alhumdallah
