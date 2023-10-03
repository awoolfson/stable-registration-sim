# checks for pairwise stabilty according to definition given in paper
def is_weakly_stable(student_dict: dict, section_dict: dict) -> (bool, list):
    
    rogue_counter = 0

    is_stable = True

    rogues = (
        []
    )  # list of tuples (student_id, section_id) that fit the rogue pair description, each will be listed twice (once for each student)

    for key in student_dict:

        cur_student = student_dict[key]
        student_rogues = []
        preferred_sections = []
        remaining_enrolled_sections = list(cur_student.enrolled_in)

        for section_id in cur_student.section_ranking:
            is_rogue = False
            cur_section = section_dict[section_id]

            # if fits traditional rogue pair definition
            if not section_id in cur_student.enrolled_in:
                if (
                    not cur_section.is_full()
                    or cur_section.get_lowest_student()[0]
                    < cur_section.score_student(cur_student)
                ):
                    is_rogue = True
                # checks if it is just a time conflict (paper definition)
                for preferred_id in preferred_sections:
                    if (
                        preferred_id in cur_student.conflicts_dict[section_id]
                        and preferred_id in cur_student.enrolled_in
                    ):
                        is_rogue = False
            else:
                remaining_enrolled_sections.remove(section_id)
                if remaining_enrolled_sections == []:
                    break

            if is_rogue:
                student_rogues.append(section_id)
            preferred_sections.append(section_id)

        rogues += list(map(lambda x: (cur_student.id, x), student_rogues))
        rogue_counter += len(student_rogues)

    if rogue_counter == 0:
        is_stable = True
    else:
        is_stable = False
    print(f"counter: {rogue_counter}")
    return (is_stable, rogue_counter, rogues)
