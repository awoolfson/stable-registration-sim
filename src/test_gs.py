import data
import test_stability
import gs

def main():
    student_dict, section_dict = data.all_from_csv(
        'test_data/test_students_2.csv',
        'test_data/test_sections_2.csv'
    )

    gs.gale_shapley_match(student_dict, section_dict)
    for student in student_dict.values():
        print(student)

    res = test_stability.is_weakly_stable(student_dict, section_dict)
    if not res[0]:
        print(res[2])

    student_dict, section_dict = data.all_from_csv(
        'test_data/test_students_2.csv',
        'test_data/test_sections_2_rogue.csv'
    )

    gs.gale_shapley_match(student_dict, section_dict)
    for student in student_dict.values():
        print(student)

    res = test_stability.is_weakly_stable(student_dict, section_dict)
    if not res[0]:
        print(res[2])
    
if __name__ == '__main__':
    main()