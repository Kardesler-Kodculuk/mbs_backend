from hashlib import md5

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
    "jury_tss_decision": "NA",
    "is_thesis_sent": 0,
    "latest_thesis_id": -1
  }
}

expected_advisor = {
  "role": "advisor",
  "username": "Kathleen",
  "advisor": {
    "user_id": 1,
    "advisor_id": 1,
    "name_": "Kathleen",
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
    "jury_tss_decision": "NA",
    "is_thesis_sent": 0,
    "latest_thesis_id": -1
  },
  "advisor": {
    "user_id": 1,
    "advisor_id": 1,
    "name_": "Kathleen",
    "surname": "Booth",
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
    "jury_tss_decision": "NA",
    "is_thesis_sent": 0,
    "latest_thesis_id": -1
}

expected_advisor_get_1 = {
    "user_id": 1,
    "advisor_id": 1,
    "name_": "Kathleen",
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
