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
#import seaborn as snsnb


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


def percentage_increase(src_folder, filename, subject, days_back):
    cols = ["ACTL"]
    # an older file
    prev_df = pd.read_csv(src_folder + filename)
    prev_data = prev_df.loc[prev_df.SUBJ == subject, cols].sum()

    # the latest file
    new_df = pd.read_csv(latest_file(src_folder))
    new_data = new_df.loc[new_df.SUBJ == subject, cols].sum()
    print("Here is the total percentage increase/decrease of enrollment from the two files:")
    increase = new_data - prev_data
    return round(((increase / prev_data) * 100),2)


# this grabs the data of a chosen course (graph and csv)
def course_data_comparison(path, semester, course_name, days_back):
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

    graph(concatDF, semester, course_name, days_back)


# this creates a bar graph displaying the data of a chosen subject
# takes 4 parameters: source folder address, subject, and the name of the file
def subject_data_comparison(path, semester, subject, days_back):
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

    graph(concatDF, semester, subject, days_back)


# graph configuration
def graph(data, semester, name, days_back):
    colors = ['b', 'r'] # colors for the graph
    groups = data.groupby(['TITLE', 'DATE'])['ACTL'].sum()  # groups the data
    # prints the standard deviation of the enrollment numbers to show how
    # widespread the data is
    actl_std = np.std(groups)
    print("The standard deviation of the # of enrolled students is: %s" % str(actl_std))
    groups.plot.barh(x='TITLE', y='ACTL', title='%s Course Enrollments for %s in a %s day period' % (semester, name, days_back), legend=True, color=colors, figsize=(14, 5))    #figsize is the size of the window
    plt.tight_layout()  # this keeps all of the data within the size of the window
    plt.show()  # required to display pop up of graph


if __name__ == '__main__':
    # starting menu
    print("Automatically loading the data...\n")


    print("What would you like to do?")
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
        if data_choice == "1":
            course_choice = input("What course did you have in mind?\n")
            if semester_choice == "1" or semester_choice == "Summer" or semester_choice == "summer":
                days_back = input("How many days do you want do you want to view the data for? ")
                course_data_comparison(src_folder, "Summer", course_choice, int(days_back))
                print("\nYour csv file and graph have been created")
            elif semester_choice == "2" or semester_choice == "Fall" or semester_choice == "fall":
                days_back = input("How many days do you want do you want to view the data for? ")
                course_data_comparison(src_folder, "Fall", course_choice, int(days_back))
                print("\nYour csv file and graph have been created")
            elif semester_choice == "3" or semester_choice == "Spring" or semester_choice == "spring":
                days_back = input("How many days do you want do you want to view the data for? ")
                course_data_comparison(src_folder, "Spring", course_choice, int(days_back))
                print("\nYour csv file and graph have been created")
            else:
                print("AwkwardError: Uhhhhhh, that wasn't even an option. Try again? I guess?")
                pass

        elif data_choice == "2":
            subject_choice = input("What subject did you have in mind?\n")
            if semester_choice == "1" or semester_choice == "Summer" or semester_choice == "summer":
                days_back = input("How many days back do you want to compare the latest to? ")
                subject_data_comparison(src_folder, "Summer", subject_choice, int(days_back))
                print("\nYour csv file and graph have been created")
            elif semester_choice == "2" or semester_choice == "Fall" or semester_choice == "fall":
                days_back = input("How many days back do you want to compare the latest to? ")
                subject_data_comparison(src_folder, "Fall", subject_choice, int(days_back))
                print("\nYour csv file and graph have been created")
            elif semester_choice == "3" or semester_choice == "Spring" or semester_choice == "spring":
                days_back = input("How many days back do you want to compare the latest to? ")
                subject_data_comparison(src_folder, "Spring", subject_choice, int(days_back))
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
