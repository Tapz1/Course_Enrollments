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


class CourseEnrollment(object):
    """docstring for CourseEnrollment.
    This grabs the enrollment numbers of a chosen course or subject (resulting in all courses under that subject) from the list of files and spits it it back out in the form of a graph and a new CSV file. This function also run the graph, statistics and emailing functions, therefore it will produce a graph, print the statistics and send an email.
    The user can use a number for days_back to determine how far back (# of files) they want to see.
    The user has to enter path of the files, the semester, the name of the course, number of days back for files, and the recipients for an emailed copy.
    """

    def __init__(self, semester, subject_course, days_back):
        super(CourseEnrollment, self).__init__()
        self.src_folder = ("D:\\SXrrmcpFiles\\SXrrmcpFiles\\")
        self.semester = semester
        self.subject_course = subject_course
        self.days_back = days_back


    def latest_file(self):
        """method for finding the last updated file"""
        list_of_files = glob.glob(self.src_folder + '*.csv')  # * means all if need specific format then *.csv
        latest_file = max(list_of_files, key=os.path.getctime)
        return latest_file


    def course_data_comparison(self, recipients):
        """
        Function example outcome:
        >>>course_data_comparison('C:\\SXrrmcpFiles\\', 'Introduction to Computer Science', 10, 'name@email.com')
            USB Drive Letter is D:\
            Automatically loading the data...

            I can send you a copy of this report to your email.
            Enter your email if you want a copy, if not hit Enter (separate multiple emails using commas):
            chris.a.tapia@gmail.com
            Now that we have that, what would you like to do?
            Whichever option # you choose will result in a graph and CSV file

                    1. View data of a specific course
                    2. View data of a specific subject (includes all courses)
                1

                For which semester would you like to see?
                    1. Summer
                    2. Fall
                    3. Spring
                2
            What course did you have in mind?
            Introduction to Computer Science
            How many days do you want do you want to view the data for? 10
            The standard deviation of the # of enrolled students is: 2.2715633383201093
            There has been a large amount of change in student enrollment
            The total percentage change (increase/decrease) of enrollment from this data is: ACTL    150.0
            dtype: float64 percent

            trying to establish a connection with the mail server...
            starting private session...
            Email successfully has been sent

            Your csv file and graph have been created
        --graph--
        (Introduction to Computer Science, Jun20-2019) - 10
        (Introduction to Computer Science, Jun19-2019) - 9
        (Introduction to Computer Science, Jun18-2019) - 9
        """

        # glob is perfect for getting all files of the same file type
        current_date = datetime.now()

        all_csv_files = glob.glob(self.src_folder + "*%s.csv" % self.semester)
        all_csv_files.sort(key=os.path.getctime)

        #latest_file = max(all_csv_files, key=os.path.getctime)
        #old_file = all_csv_files[-days_back]
        #file_name_list = [latest_file, old_file]


        file_list = []  # new file list
        # columns in the DataFrame (df)
        cols = ['DATE', 'TITLE', 'CRN', 'ACTL']

        for filename in all_csv_files[-self.days_back:]:
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
            data = df.loc[df.TITLE == self.subject_course, cols]
            file_list.append(data)


        # file creation
        # concatDF takes the list data and neatly puts it all in one file
        concatDF = pd.concat(file_list, axis=0)
        concatDF.columns=cols
        concatDF.to_csv("%s %s Enrollment Data - %s day comparison.csv" % (self.semester, self.subject_course, str(self.days_back)), index=None)

        graph_name = ("%s %s Enrollment Data - %s day comparison.pdf" % (self.semester, self.subject_course, str(self.days_back)))
        # the graph
        CourseEnrollment.graph(self, concatDF, graph_name)

        new_file_name = ("%s %s Enrollment Data - %s day comparison.csv" % (self.semester, self.subject_course, str(self.days_back)))

        # the new CSV file and the graph
        files_to_send = [new_file_name, graph_name]

        # params: subject, body, filename, recipients
        send_email(("%s %s Enrollment Data" % (self.semester, self.subject_course)), CourseEnrollment.course_statistics(self, all_csv_files, concatDF), files_to_send, recipients.split(','))


    def subject_data_comparison(self, recipients):
        """
        Function example outcome:
        >>>subject_data_comparison('C:\\SXrrmcpFiles\\', 'CIS', 10, 'name@email.com')
            USB Drive Letter is D:\
            Automatically loading the data...

            I can send you a copy of this report to your email.
            Enter your email if you want a copy, if not hit Enter (separate multiple emails using commas):
            name@email.com
            Now that we have that, what would you like to do?
            Whichever option # you choose will result in a graph and CSV file

                    1. View data of a specific course
                    2. View data of a specific subject (includes all courses)
                2
                For which semester would you like to see?
                    1. Summer
                    2. Fall
                    3. Spring
                2
            What subject did you have in mind?
            CIS
            How many days back do you want to compare the latest to? 10
            trying to establish a connection with the mail server...
            starting private session...
            Email successfully has been sent

            Your csv file and graph have been created
        --graph--
        (Introduction to Python, Jun20-2019) - 4
        (Introduction to Python, Jun07-2019) - 3
        (Introduction to Computer Science, Jun20-2019) - 10
        (Introduction to Computer Science, Jun07-2019) - 4
        """

        current_date = datetime.now()

        all_csv_files = glob.glob(self.src_folder + "*%s.csv" % self.semester)
        all_csv_files.sort(key=os.path.getctime)

        latest_file = max(all_csv_files, key=os.path.getctime)
        old_file = all_csv_files[-self.days_back]
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
            data = df.loc[df.SUBJ == self.subject_course, cols]
            file_list.append(data)

        # file creation
        # concatDF takes the list data and neatly puts it all in one file
        concatDF = pd.concat(file_list, axis=0)
        concatDF.columns=cols
        concatDF.to_csv("%s %s Enrollment Data - %s day comparison.csv" % (self.semester, self.subject_course, str(self.days_back)), index=None)


        graph_name = ("%s %s Enrollment Data - %s day comparison.pdf" % (self.semester, self.subject_course, str(self.days_back)))

        CourseEnrollment.graph(self, concatDF, graph_name)

        new_file_name = ("%s %s Enrollment Data - %s day comparison.csv" % (self.semester, self.subject_course, str(self.days_back)))

        print(CourseEnrollment.subject_statistics(self, concatDF))
        # the new CSV file and the graph
        files_to_send = [new_file_name, graph_name]
        body = "Here is your %s data comparison on all the courses in %s" % (str(self.days_back), self.subject_course)
        # sends email - params: subject, body, filename, recipients
        send_email(("%s %s Enrollment Data" % (self.semester, self.subject_course)), body, files_to_send, recipients.split(','))


    def graph(self, data, graph_name):
        """graph configuration"""
        colors = ['b', 'r'] # colors for the graph
        groups = data.groupby(['TITLE', 'DATE'])['ACTL'].sum()  # groups the data

        groups.plot.barh(x='TITLE', y='ACTL', title='%s Course Enrollments for %s in a %s day period' % (self.semester, self.subject_course, self.days_back), legend=True, color=colors, figsize=(14, 5))    #figsize is the size of the window
        plt.tight_layout()  # this keeps all of the data within the size of the window
        plt.savefig(graph_name)
        plt.show()  # required to display pop up of graph


    def subject_statistics(self, data):
        """testing with stats for subject"""
        cols = ["ACTL"]

        groups = data.groupby(['TITLE', 'DATE'])
        #type(groups)
        head = (groups.describe().head())
        head.to_csv("Test.csv")



    def course_statistics(self, data_list, data):
        """uses numpy to generate responses of the data"""
        cols = ["ACTL"]
        # an older file
        old_df = pd.read_csv(data_list[-self.days_back])
        # drops duplicate data, identified by its CRN
        old_df.drop_duplicates(subset = 'CRN', keep='first', inplace=True)
        old_data = oldest_df.loc[old_df.TITLE == self.subject_course, cols].sum()

        # the latest file
        new_df = pd.read_csv(data_list[-1])
        new_df.drop_duplicates(subset = 'CRN', keep='first', inplace=True)
        new_data = new_df.loc[new_df.TITLE == self.subject_course, cols].sum()

        data_change = new_data - old_data
        percentage = round(((data_change / old_data) * 100),2)
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
                # getting the self params for the class
                course = CourseEnrollment("Summer", course_choice, int(days_back))
                # adding var to function specific param
                course.course_data_comparison(recipients)
                print("\nYour csv file and graph have been created")
            elif semester_choice == "2" or semester_choice == "Fall" or semester_choice == "fall":
                days_back = input("How many days do you want do you want to view the data for? ")
                course = CourseEnrollment("Fall", course_choice, int(days_back))
                course.course_data_comparison(recipients)
                print("\nYour csv file and graph have been created")
            elif semester_choice == "3" or semester_choice == "Spring" or semester_choice == "spring":
                days_back = input("How many days do you want do you want to view the data for? ")
                course = CourseEnrollment("Spring", course_choice, int(days_back))
                course.course_data_comparison(recipients)
                print("\nYour csv file and graph have been created")
            else:
                print("AwkwardError: Uhhhhhh, that wasn't even an option. Try again? I guess?")
                pass

        # multiple course comparison
        elif data_choice == "2":
            subject_choice = input("What subject did you have in mind?\n")
            if semester_choice == "1" or semester_choice == "Summer" or semester_choice == "summer":
                days_back = input("How many days back do you want to compare the latest to? ")
                course = CourseEnrollment("Summer", subject_choice, int(days_back))
                course.subject_data_comparison(recipients)
                print("\nYour csv file and graph have been created")
            elif semester_choice == "2" or semester_choice == "Fall" or semester_choice == "fall":
                days_back = input("How many days back do you want to compare the latest to? ")
                course = CourseEnrollment("Fall", subject_choice, int(days_back))
                course.subject_data_comparison(recipients)
                print("\nYour csv file and graph have been created")
            elif semester_choice == "3" or semester_choice == "Spring" or semester_choice == "spring":
                days_back = input("How many days back do you want to compare the latest to? ")
                course = CourseEnrollment("Spring", subject_choice, int(days_back))
                course.subject_data_comparison(recipients)
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
