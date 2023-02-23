import pandas as pd
from Student import Student
from CourseSection import CourseSection

"""
TODO
- create a refresh preferences method for students that puts the courses that fit into credits on top, 
  will eventually handle backups etc
- test Gale-Shapley method for functionality and stabiliy, create more individualized test files/cases
  this will require a far more comprehensive printing/testing method, could be high priority
  - add the stability tester method
"""

section_df = pd.DataFrame() # dataframe serves as intemediary between CSV and dict
section_dict = {} # source of truth during program
student_df = pd.DataFrame()
student_dict = {}

def student_dict_to_df():
    for key in student_dict:
        update_student_df(student_dict[key])

def section_dict_to_df():
    for key in section_dict:
        update_section_df(section_dict[key])

def get_df_student(id: int):
    row = student_df.loc[id] # figure out how to make this work next!
    student = Student(id = id, name = row[0], base_score = int(row[1]))
    student.set_section_ranking(row[2].split(" "))
    return student

def get_df_section(id: int):
    print(section_df.index)
    row = section_df.loc[id]
    section = CourseSection(id = id, course_name = row[0],
                                                capacity = int(row[1]), credits = int(row[2]))
    return section

def update_student_df(student: Student):
    # currently only updates section ranking and schedule
    student_df.at[student.id, 3] = str(student.section_ranking)
    student_df.at[student.id, 4] = str(student.schedule)
    
def update_section_df(section: CourseSection):
    # currently only updates roster, will need to update removed if I end up using it
    roster = []
    for student in section.roster_pq:
        roster.append(student.id)
    section_df.at[section.id, 'roster_ids'] = str(roster)[1:-1]

def add_student_to_section(student: Student, section: CourseSection):
    student.join_section(section)
    section.enroll(student)
    return student, section

def try_enrolling(student: Student, section: CourseSection):
    
    # checks if a student has enough credits, if course has space or student is better than current enrolled
    # returns updated objects
    
        section.swapped_out = (False, 0) # default to no student swapping
        if student.credits_enrolled + section.credits > student.credit_limit: # this is maybe redundant with  new is free method?
            print(f'student #{student.id} could not enroll in section #{section.id}'
                  +' because they are taking too many credits')
            return student, section
        elif section.is_full():
            if section.score_student(student) > section.return_lowest_student().section_score:
                removed_student = section.pop_lowest_student() # currently does nothing, try new addition to removed dict?
                section.swapped_out = (True, removed_student.id)
                print(f'student:\n {removed_student}\n swapped out for\n {student}\n in section:\n {section}')
                return add_student_to_section(student, section)
            else:
                print(f'student #{student.id} could not enroll in section #{section.id}'
                  +' because the section is full of higher priority students')
                return student, section
        else:
            return add_student_to_section(student, section)
        
def try_enrolling_next_section(student: Student):
    
    # handles student top section pointer and calls try_enrolling
    
    proposed_section = section_dict[student.get_top_section_id()]
    print(f"trying to enroll {student.name} in {proposed_section.course_name}")
    student.increment_next_section()
    return try_enrolling(student, proposed_section)
        
def Gale_Shapley():
    
    # initialize and populate free students list
    
    free_students = []
    for id in student_dict:
        free_students.append(id)
        
    # look at last student in free list
    
    while len(free_students) > 0:
        to_pop = True # this determines if a student has been swapped out and a pop on the free student list is not needed
        cur_student = student_dict[free_students[-1]]
        print(f"cur_student: {cur_student.name}\n")
        
        # while student has more sections to propose to
        
        while not cur_student.is_finished_proposing():
            
            # if they have no more credits they can fulfill
            
            if not cur_student.has_credits_to_fill(section_dict[cur_student.get_top_section_id()].credits):
                print(f"all credits fulfilled!\n")
                break
            
            # try enrolling student in favorite section
            
            updated_agents = try_enrolling_next_section(cur_student)
            cur_student_new, proposed_section_new = updated_agents[0], updated_agents[1]
            
            # update dictionaries with returned student and section objects
            
            student_dict[cur_student.id] = cur_student_new
            section_dict[proposed_section_new.id] = proposed_section_new
            
            print(f"cur_student_new:\n\n {cur_student_new}\n\n proposed_section_new:\n\n {proposed_section_new}")
            
            # if a student in the section has been replaced
            
            if proposed_section_new.swapped_out[0] == True:
                to_pop = False
                swapped_student = student_dict[proposed_section_new.swapped_out[1]]
                swapped_student.leave_section(proposed_section_new)
                student_dict[swapped_student.id] = swapped_student
                free_students.append(swapped_student.id) # it should be fine anyway if this is duplicate?
                cur_student = cur_student_new
                break # break so the swapped student can start proposing
            
            print(f"proposed_section_new queue:\n\n {proposed_section_new.roster_pq}")
            
            # update the student object for the loop
        if to_pop:
            free_students.pop()
        
def is_pairwise_stable():
    
    # to be tested
    
    for key in student_dict:
        cur_student = student_dict[key]

        cur_student_remaining_schedule = cur_student.schedule # used to check if iteration has passed the lowest ranked course in schedule
        
        for index, section_id in enumerate(cur_student.section_ranking):
            
            if not section_id in cur_student.schedule:
                if not section_dict[section_id].is_full():
                    return False
                else:
                    # ok this is very ugly, fix this and make a variable for cur_section
                    if section_dict[section_id].return_lowest_student().section_score < section_dict[section_id].score_student(cur_student):
                        return False
            else:
                cur_student_remaining_schedule.remove(section_id)
                if len(cur_student_remaining_schedule) == 0:
                    continue # move on to next student if all prefered sections have been examined
        return True

def main():
    global student_dict
    global section_dict
    global student_df
    global section_df
    
    student_list = []
    student_df = pd.read_csv("../test_data/test_students_2.csv",  delimiter = ",")
    student_df.set_index("id", inplace = True)

    print(student_df)

    for index, row in student_df.iterrows():
        new_student = Student(id = index, name = row[0], base_score = int(row[1]))
        new_student.set_section_ranking(row[2].split(" "))
        student_list.append(new_student)
        student_dict[new_student.id] = new_student
        
    section_list = []
    section_df = pd.read_csv("../test_data/test_sections_2.csv")
    section_df.set_index("id", inplace = True)

    print(section_df)

    for index, row in section_df.iterrows():
        new_section = CourseSection(id = index, course_name = row[0],
                                                capacity = int(row[1]), credits = int(row[2]))
        section_list.append(new_section)
        section_dict[new_section.id] = new_section
        
        
    for key in student_dict:
        print(student_dict[key])
    for key in section_dict:
        print(section_dict[key])
        
    Gale_Shapley()
    
    print("""post GS students
        ------------------------\n
          """)

    for key in student_dict:
        print(student_dict[key])
        
    print("""post GS sections
        ------------------------\n
          """)
    
    for key in section_dict:
        print(section_dict[key])
        
main()
    