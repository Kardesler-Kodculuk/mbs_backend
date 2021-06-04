expected_student = {
  "role": "student",
  "username": "Barbara",
  "student": {
    "user_id": 2,
    "student_id": 2,
    "name_": "Barbara",
    "surname": "Liskov",
    "email": "studenttest2@std.iyte.edu.tr",
    "department": "Computer Engineering",
    "is_approved": 0,
    "has_proposed": 0,
    "semester": 2,
    "program_name": "Computer Engineering",
    "thesis_topic": "Graph Visualisation",
    "graduation_status": "NA",
    "has_dissertation": False,
    "is_thesis_sent": 0,
    "latest_thesis_id": -1,
    'is_advisors_recommended': True
  }
}

expected_advisor = {
  "role": "advisor",
  "username": "Kathleen",
  "advisor": {
    "user_id": 1,
    "advisor_id": 1,
    "name_": "Kathleen",
    "is_jury": False,
    "surname": "Booth",
    "email": "advisortest@iyte.edu.tr",
    "department": "Computer Engineering",
    "doctoral_specialty": "Systems Programming"
  }
}

expected_advisor_of_student = {
    "advisor": {
        "user_id": 1,
        "advisor_id": 1,
        "name_": "Kathleen",
        "is_jury": False,
        "surname": "Booth",
        "email": "advisortest@iyte.edu.tr",
        "department": "Computer Engineering",
        "doctoral_specialty": "Systems Programming"
    }
}

expected_student_advisor = {
  "role": "student",
  "username": "Scott",
  "student": {
    "user_id": 0,
    "student_id": 0,
    "name_": "Scott",
    "surname": "Aaronson",
    "email": "studenttest@std.iyte.edu.tr",
    "department": "Computer Engineering",
    "is_approved": 1,
    "has_proposed": 1,
    "semester": 2,
    "program_name": "Computer Engineering",
    "thesis_topic": "Graph Visualisation",
    "graduation_status": "NA",
    "has_dissertation": False,
    "is_thesis_sent": 0,
    "latest_thesis_id": -1,
    'is_advisors_recommended': True
  },
  "advisor": {
    "user_id": 1,
    "advisor_id": 1,
    "name_": "Kathleen",
    "surname": "Booth",
    "is_jury": False,
    "email": "advisortest@iyte.edu.tr",
    "department": "Computer Engineering",
    "doctoral_specialty": "Systems Programming"
  }
}

expected_student_get_0 = {
    "user_id": 0,
    "student_id": 0,
    "name_": "Scott",
    "surname": "Aaronson",
    "email": "studenttest@std.iyte.edu.tr",
    "department": "Computer Engineering",
    "is_approved": 1,
    "has_proposed": 1,
    "semester": 2,
    "program_name": "Computer Engineering",
    "thesis_topic": "Graph Visualisation",
    "graduation_status": "NA",
    "has_dissertation": False,
    "is_thesis_sent": 0,
    "latest_thesis_id": -1,
    'is_advisors_recommended': True
}

expected_advisor_get_1 = {
    "user_id": 1,
    "advisor_id": 1,
    "name_": "Kathleen",
    "is_jury": False,
    "surname": "Booth",
    "email": "advisortest@iyte.edu.tr",
    "department": "Computer Engineering",
    "doctoral_specialty": "Systems Programming"
}

expected_proposals = [
    {
        "proposal_id": 0,
        "advisor_id": 3,
        "student_id": 4
    },
    {
        "proposal_id": 1,
        "advisor_id": 3,
        "student_id": 5
    }
]

expected_recommendations = [
    {
        "recommendation_id": 0,
        "advisor_id": 1,
        "student_id": 2
    },
    {
        "recommendation_id": 1,
        "advisor_id": 3,
        "student_id": 2
    }

]


expected_theses_list = [
    0,
    1
]

expected_thesis_metadata_get = {
    "thesis_id": 0,
    "plagiarism_ratio": 15,
    "thesis_topic": "Artificial Intelligence",
    "original_name": "grey_thesis_example0.pdf",
    "submission_date": 1621129273
}

expected_pdf_file_name = 'theses/grey_thesis_example0.pdf'

expected_pdf_upload_resp = {'thesis_topic': 'Artificial Intelligence'}

expected_dbr = {
    "role": "DBR",
    "username": "Roddy",
    "DBR": {
        "user_id": 18,
        "dbr_id": 18,
        "name_": "Roddy",
        "surname": "Welman",
        "email": "welman@pers.iyte.edu.tr",
        "department": "Computer Engineering"
    }
}

expected_jury = {
    "role": "jury",
    "username": "Eileen",
    "jury": {
        "user_id": 20,
        "jury_id": 20,
        "is_approved": 1,
        "name_": "Eileen",
        "surname": "O'Brien",
        "email": "obrien@metu.edu.tr",
        "department": "Not Available",
        "institution": "Middle Eastern Technical University",
        "phone_number": "+90 5XX XXX XX XX",
        "is_appointed": 1
    }
}

expected_student_defending_list = {
    'students': [

    ],
    'defenders': [
        15,
        17
    ]
}

expected_student_department_list = {
    'students': [
        21,
        22
    ],
    'defenders': []
}

expected_jury_info = {
        "user_id": 20,
        "jury_id": 20,
        "is_approved": 1,
        "name_": "Eileen",
        "surname": "O'Brien",
        "email": "obrien@metu.edu.tr",
        "department": "Not Available",
        "institution": "Middle Eastern Technical University",
        "phone_number": "+90 5XX XXX XX XX",
        "is_appointed": 1
    }

expected_student_info_from_jury_advisor = {
    'students': [
        21,
        22
    ],
    'defenders': [
        22,
        21
    ]
}

expected_dissertation = {
    "student_id": 22,
    "jury_ids": [
        23,
        20
    ],
    "jury_date": 1621129276,
    "status": 'Undecided'
}

expected_jury_members = {"jury_members": [23, 24, 25, 20]}

jury_add_command = {
    "name_": "Charlotte Froese",
    "surname": "Fischer",
    "email": "fischer@miskatonic.edu.tr",
    "institution": "Miskatonic University",
    "phone_number": "+90 5XX XXX XX XX"
}

dissertation_add_json = {
    "jury_members": [
        20
    ],
    "dissertation_date": 234243
}

dissertation_add_json_with_new_members = {
    **dissertation_add_json,
    "new_members": [jury_add_command, ],
    "dissertation_date": 234243
}

dissertation_expected_json = {
    "jury_ids": [
        20,
        16
    ],
    "jury_date": 234243,
    "status": "Pending",
    "student_id": 26
}


advisors_list = {
    "advisors": [
        1,
        3,
        6,
        9,
        16
    ]
}

recommended_advisors = {
  "recommended_advisors": [
      1,
      3
  ]
}

expected_jury_temp = {
        "user_id": -1, # Must set this.
        "jury_id": -1,  # Must set this
        "is_approved": 0,
        "name_": "Charlotte Froese",
        "surname": "Fischer",
        "email": "fischer@miskatonic.edu.tr",
        "institution": "Miskatonic University",
        "phone_number": "+90 5XX XXX XX XX",
        "department": "Computer Engineering",
        "is_appointed": 1
}

students_without_recommendations = {"students_without_recommendations": [27]}  # For history.

expected_sparrowhawk = {
  "role": "student",
  "username": "Ged",
  "student": {
    "user_id": 27,
    "student_id": 27,
    "name_": "Ged",
    "surname": "Sparrowhawk",
    "email": "sparrowhawk@std.iyte.edu.tr",
    "department": "History",
    "is_approved": 1,
    "has_proposed": 0,
    "semester": 2,
    "program_name": "History",
    "thesis_topic": "Earthsea History Before Erreth-Akbe",
    "graduation_status": "NA",
    "has_dissertation": False,
    "is_thesis_sent": 0,
    "latest_thesis_id": -1,
    'is_advisors_recommended': False
  }
}

