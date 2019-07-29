"""
Programmer = Chris Tapia
Description = Enrollment data from csv files
"""

import os
from os import listdir
from os.path import isfile, join
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import glob
from string import ascii_uppercase
from matplotlib import pyplot as plt

from send_email import send_email


# method for finding the last updated file
def latest_file(src_folder):
    list_of_files = glob.glob(src_folder + '*.csv')  # * means all if need specific format then *.csv
    latest_file = max(list_of_files, key=os.path.getctime)
    return latest_file


# method for finding the USB drive
def drive_location():
    for USBPATH in ascii_uppercase:
        # have to place a .txt file in the USB
        if os.path.exists('%s:\\ProgramFile.txt' % USBPATH):
            USBPATH = '%s:\\' % USBPATH
            print('USB Drive Letter is', USBPATH)
            return USBPATH + ""
    return ""


# hard coded variable for testing purposes... should not change
src_folder = (drive_location() + "SXrrmcpFiles\\SXrrmcpFiles\\")
#src_folder = "C:\\Users\\chris\\Downloads\\SXrrmcpFiles\\"


# this grabs the data of a chosen course (graph and csv)
def course_data_comparison(path, semester, course_name, days_back, recipients):
    # glob is perfect for getting all files of the same file type
    current_date = datetime.now()

    all_csv_files = glob.glob(path + "*%s.csv" % semester)
    all_csv_files.sort(key=os.path.getctime)

    #latest_file = max(all_csv_files, key=os.path.getctime)
    #old_file = all_csv_files[-days_back]
    #file_name_list = [latest_file, old_file]


    file_list = []  # new file list
    # columns in the DataFrame (df)
    cols = ['DATE', 'TITLE', 'CRN', 'ACTL']

    for filename in all_csv_files[-days_back:]:
        # name of file, not just the path
        name_of_file = os.path.basename(filename)
        # using Pandas to read the files, df is the DataFrame
        df = pd.read_csv(filename).assign(filename=name_of_file)
        # sorting the data in the DF by the Date of the file

        if "_Summer" in name_of_file:
            new_name = name_of_file.replace(name_of_file[-13:], "-%s" % ("20" + name_of_file[5:7]))
        elif "_Fall" in name_of_file:
            new_name = name_of_file.replace(name_of_file[-11:], "-%s" % ("20" + name_of_file[5:7]))
        elif "_Spring" in name_of_file:
            new_name = name_of_file.replace(name_of_file[-13:], "-%s" % ("20" + name_of_file[5:7]))
        # adds another column "DATE" to identify which file the data is from
        # and to group them
        df["DATE"] = new_name
        df.sort_values('DATE', inplace=True)
        # drops duplicate data, identified by its CRN
        df.drop_duplicates(subset = 'CRN', keep='first', inplace=True)
        # if statement to shorten the name of the file and add make it more readable
        # df.loc is a boolean statement that grabs data based on TITLE name
        data = df.loc[df.TITLE == course_name, cols]
        file_list.append(data)


    # file creation
    # concatDF takes the list data and neatly puts it all in one file
    concatDF = pd.concat(file_list, axis=0)
    concatDF.columns=cols
    concatDF.to_csv("%s %s Enrollment Data - %s day comparison.csv" % (semester, course_name, str(days_back)), index=None)

    graph_name = ("%s %s Enrollment Data - %s day comparison.pdf" % (semester, course_name, str(days_back)))
    # the graph
    graph(concatDF, semester, course_name, days_back, graph_name)

    new_file_name = ("%s %s Enrollment Data - %s day comparison.csv" % (semester, course_name, str(days_back)))

    # the new CSV file and the graph
    files_to_send = [new_file_name, graph_name]

    # params: subject, body, filename, recipients
    send_email(("%s %s Enrollment Data" % (semester, course_name)), statistics(all_csv_files, course_name, concatDF, days_back), files_to_send, recipients.split(','))

# this creates a bar graph displaying the data of a chosen subject
# takes 4 parameters: source folder address, subject, and the name of the file
def subject_data_comparison(path, semester, subject, days_back, recipients):
    current_date = datetime.now()

    all_csv_files = glob.glob(path + "*%s.csv" % semester)
    all_csv_files.sort(key=os.path.getctime)

    latest_file = max(all_csv_files, key=os.path.getctime)
    old_file = all_csv_files[-days_back]
    file_name_list = [latest_file, old_file]

    file_list = []  # new file list

    # columns in the DataFrame (df)
    cols = ['DATE', 'TITLE', 'CRN', 'ACTL']

    # this loop indexes Nth file and latest file from list
    for filename in file_name_list:
        # name of file, not just the path
        name_of_file = os.path.basename(filename)
        # using Pandas to read the files, df is the DataFrame
        df = pd.read_csv(filename).assign(filename=name_of_file)
        # sorting the data in the DF by the Class Title
        df.sort_values('TITLE', inplace=True)
        # drops duplicate data, identified by its CRN
        df.drop_duplicates(subset = 'CRN', keep='first', inplace=True)

        # if statement to shorten the name of the file and add make it more readable
        if "_Summer" in name_of_file:
            new_name = name_of_file.replace(name_of_file[-13:], "-%s" % (current_date.year))
        elif "_Fall" in name_of_file:
            new_name = name_of_file.replace(name_of_file[-11:], "-%s" % (current_date.year))
        elif "_Spring" in name_of_file:
            new_name = name_of_file.replace(name_of_file[-13:], "-%s" % (current_date.year))

        # adds another column "DATE" to identify which file the data is from
        # and to group them
        df["DATE"] = new_name
        # df.loc is a boolean statement that grabs data based on subject name
        data = df.loc[df.SUBJ == subject, cols]
        file_list.append(data)

    # file creation
    # concatDF takes the list data and neatly puts it all in one file
    concatDF = pd.concat(file_list, axis=0)
    concatDF.columns=cols
    concatDF.to_csv("%s %s Enrollment Data - %s day comparison.csv" % (semester, subject, str(days_back)), index=None)

    graph_name = ("%s %s Enrollment Data - %s day comparison.pdf" % (semester, subject, str(days_back)))

    graph(concatDF, semester, subject, days_back, graph_name)

    new_file_name = ("%s %s Enrollment Data - %s day comparison.csv" % (semester, subject, str(days_back)))

    # the new CSV file and the graph
    files_to_send = [new_file_name, graph_name]

    # sends email - params: subject, body, filename, recipients
    send_email(("%s %s Enrollment Data" % (semester, subject)), statistics(concatDF), files_to_send, recipients.split(','))


# graph configuration
def graph(data, semester, name, days_back, graph_name):
    colors = ['b', 'r'] # colors for the graph
    groups = data.groupby(['TITLE', 'DATE'])['ACTL'].sum()  # groups the data

    groups.plot.barh(x='TITLE', y='ACTL', title='%s Course Enrollments for %s in a %s day period' % (semester, name, days_back), legend=True, color=colors, figsize=(14, 5))    #figsize is the size of the window
    plt.tight_layout()  # this keeps all of the data within the size of the window
    plt.savefig(graph_name)
    plt.show()  # required to display pop up of graph


# uses numpy to generate responses of the data
def statistics(data_list, course_name, data, days_back):
    cols = ["ACTL"]
    # an older file
    oldest_df = pd.read_csv(data_list[-days_back])
    # drops duplicate data, identified by its CRN
    oldest_df.drop_duplicates(subset = 'CRN', keep='first', inplace=True)
    oldest_data = oldest_df.loc[oldest_df.TITLE == course_name, cols].sum()

    # the latest file
    new_df = pd.read_csv(data_list[-1])
    new_df.drop_duplicates(subset = 'CRN', keep='first', inplace=True)
    new_data = new_df.loc[new_df.TITLE == course_name, cols].sum()

    data_change = new_data - oldest_data
    percentage = round(((data_change / oldest_data) * 100),2)
    percent_detail = "The total percentage change (increase/decrease) of enrollment from this data is: %s percent \n" % str(percentage)

    groups = data.groupby(['TITLE', 'DATE'])['ACTL'].sum()  # groups the data
    # prints the standard deviation of the enrollment numbers to show how
    # widespread the data is
    actl_std = np.std(groups)
    print("The standard deviation of the # of enrolled students is: %s" % str(actl_std))

    if actl_std < .5:
        print("There hasn't been any significant change in student enrollment\n" + percent_detail)
        return "There hasn't been any significant change in student enrollment\n" + percent_detail

    elif actl_std < 1 and actl_std > .5:
        print("There has been a small amount of change in student enrollment!\n" + percent_detail)
        return "There has been a small amount of change in student enrollment!\n" + percent_detail

    elif actl_std > 1:
        print("There has been a large amount of change in student enrollment\n" + percent_detail)
        return "There has been a large amount of change in student enrollment\n" + percent_detail


if __name__ == '__main__':
    # starting menu
    print("Automatically loading the data...\n")

    print("I can send you a copy of this report to your email.")
    # gathers email addresses to send data
    recipients = input("Enter your email if you want a copy, if not hit Enter (separate multiple emails using commas):\n")
    print("Now that we have that, what would you like to do?")
    print("Whichever option # you choose will result in a graph and CSV file")
    data_choice = input("""
        1. View data of a specific course
        2. View data of a specific subject (includes all courses)
    """)

    semester_choice = input("""
    For which semester would you like to see?
        1. Summer
        2. Fall
        3. Spring
    """)
    try:
        # single course data
        if data_choice == "1":
            course_choice = input("What course did you have in mind?\n")
            if semester_choice == "1" or semester_choice == "Summer" or semester_choice == "summer":
                days_back = input("How many days do you want do you want to view the data for? ")
                course_data_comparison(src_folder, "Summer", course_choice, int(days_back), recipients)
                print("\nYour csv file and graph have been created")
            elif semester_choice == "2" or semester_choice == "Fall" or semester_choice == "fall":
                days_back = input("How many days do you want do you want to view the data for? ")
                course_data_comparison(src_folder, "Fall", course_choice, int(days_back), recipients)
                print("\nYour csv file and graph have been created")
            elif semester_choice == "3" or semester_choice == "Spring" or semester_choice == "spring":
                days_back = input("How many days do you want do you want to view the data for? ")
                course_data_comparison(src_folder, "Spring", course_choice, int(days_back), recipients)
                print("\nYour csv file and graph have been created")
            else:
                print("AwkwardError: Uhhhhhh, that wasn't even an option. Try again? I guess?")
                pass

        # multiple course comparison
        elif data_choice == "2":
            subject_choice = input("What subject did you have in mind?\n")
            if semester_choice == "1" or semester_choice == "Summer" or semester_choice == "summer":
                days_back = input("How many days back do you want to compare the latest to? ")
                subject_data_comparison(src_folder, "Summer", subject_choice, int(days_back), recipients)
                print("\nYour csv file and graph have been created")
            elif semester_choice == "2" or semester_choice == "Fall" or semester_choice == "fall":
                days_back = input("How many days back do you want to compare the latest to? ")
                subject_data_comparison(src_folder, "Fall", subject_choice, int(days_back), recipients)
                print("\nYour csv file and graph have been created")
            elif semester_choice == "3" or semester_choice == "Spring" or semester_choice == "spring":
                days_back = input("How many days back do you want to compare the latest to? ")
                subject_data_comparison(src_folder, "Spring", subject_choice, int(days_back), recipients)
                print("\nYour csv file and graph have been created")
            else:
                print("AwkwardError: Uhhhhhh, that wasn't even an option. Try again? I guess?")
                pass

        else:
            print("AwkwardError: Uhhhhhh, that wasn't even an option. Try again? I guess?")
            pass

    except FileNotFoundError:
        print("Sorry, this file either GHOSTED you like my ex-gf or just isn't here! :')'")

    except IndexError:
        print("Sorry, either you're from the FUTURE or that date you chose is just out of range! :D")

    except ValueError:
        print("Sorry, couldn't process. That wasn't even a number! Try actually entering a number next time?")
