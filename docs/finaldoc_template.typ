// template.typ

// ── DOCUMENT SETUP ────────────────────────────────────────────────────
#let project(body) = {
  set page(
    paper: "a4",
    margin: (x: 2.5cm, y: 2.5cm),
  )
  set text(
    font: "Times New Roman",
    size: 12pt,
    lang: "en"
  )
  set par(justify: true)

  body
}

// ── Helper functions ──────────────────────────────────────────────────
#let signature-line(width: 200pt) = {
  line(length: width, stroke: 0.5pt)
}

// ── 1. COVER PAGE ─────────────────────────────────────────────────────
#let cover-page(title, student-name, student-id, location, sub-date) = page[
  #align(center)[
    #v(1cm)
    #text(size: 18pt, weight: "bold")[#title]
   
    #v(1cm)
    #text(size: 14pt)[BITS ZC4999T: Capstone Project]
   
    #v(1cm)
    by
   
    #v(0.5cm)
    #text(weight: "bold", size: 14pt)[#student-name] \
    #text(weight: "bold", size: 12pt)[#student-id]
   
    #v(2cm)
    Capstone Project work carried out at \
    #text(weight: "bold")[#location]
   
    #v(1fr)
   
    #rect(width: 3.5cm, height: 3.5cm, stroke: none)[
      #image("bitslogo.png", width: 3.5cm)
    ]
   
    #v(0.5cm)
    #text(size: 16pt, weight: "bold")[BIRLA INSTITUTE OF TECHNOLOGY & SCIENCE] \
    #text(size: 14pt, weight: "bold")[PILANI (RAJASTHAN)]
   
    #v(0.5cm)
    #text(weight: "bold")[#sub-date]
    #v(1cm)
  ]
]

// ── 2. TITLE PAGE (inner) ─────────────────────────────────────────────
#let title-page(title, student-name, student-id, location, mentor-name, mentor-title, mentor-org, sub-date) = page[
  #align(center)[
    #v(1cm)
    #text(size: 16pt, weight: "bold")[#title]
   
    #v(0.5cm)
    #text(size: 12pt)[BITS ZC4999T: Capstone Project]
 
    #v(0.8cm)
    by
   
    #v(0.5cm)
    #text(weight: "bold", size: 13pt)[#student-name] \
    #text(weight: "bold")[#student-id]
   
    #v(1cm)
    Capstone Project work carried out at \
    #text(weight: "bold")[#location]
   
    #v(1cm)
    Submitted in partial fulfillment of B.Sc. \
    (Design and Computing) degree programme
   
    #v(1cm)
    Under the Supervision of
   
    #v(0.5cm)
    #text(weight: "bold")[#mentor-name, #mentor-title] \
    #mentor-org
   
    #v(1fr)
   
    #rect(width: 3.5cm, height: 3.5cm, stroke: none)[
      #image("bitslogo.png", width: 3.5cm)
    ]
   
    #text(size: 14pt, weight: "bold")[BIRLA INSTITUTE OF TECHNOLOGY & SCIENCE] \
    #text(size: 12pt, weight: "bold")[PILANI (RAJASTHAN)]
   
    #v(0.5cm)
    #text(weight: "bold")[#sub-date]
    #v(1cm)
  ]
]

// ── 3. CERTIFICATE ────────────────────────────────────────────────────
#let certificate(title, student-name, student-id, mentor-name, mentor-title, mentor-org, comp-date) = page[
  #align(center)[
    #underline[ #text(size: 16pt, weight: "bold")[CERTIFICATE]]
  ]
  #v(2cm)
 
  This is to certify that the Capstone Project entitled #strong(title) and submitted by #strong(student-name) having BITS ID No – #strong(student-id) for the partial fulfilment of the requirements of B.Sc. (Design and Computing) degree programme of BITS, embodies the Bonafide work done by him/her under my supervision.
 
  #v(2cm)
 
  #align(left)[
    #rect(width: 5cm, height: 2cm, stroke: 1pt)[*#mentor-name Signature*]
   
    #signature-line(width: 250pt) \
    #strong("Signature of the Mentor") \
   
    #v(0.5cm)
    #grid(
      columns: (auto, auto),
      gutter: 10pt,
      [Place:], [Canada],
      [Date:], [#comp-date],
    )
    #v(0.5cm)
    _#mentor-name, #mentor-title, #mentor-org _ \
    #text(size: 10pt)[Name, Designation & Organization & Location]
  ]
]

// ── 4. ABSTRACT ───────────────────────────────────────────────────────
#let abstract-page(title, student-name, student-id, student-email, location, mentor-name, mentor-org, mentor-email, comp-date) = page[
  #align(center)[
    #text(weight: "bold")[Birla Institute of Technology & Science, Pilani] \
    Work-Integrated Learning Programmes Division \
   
    #v(0.5cm)
    BITS ZC499T: Capstone Project \
    #v(0.5cm)
    #underline[ #text(size: 14pt, weight: "bold")[ABSTRACT]]
  ]
 
  #v(1cm)
 
  #table(
    columns: (40%, 60%),
    stroke: none,
    align: (left, left),
    [ID No.:], [#student-id],
    [NAME OF THE STUDENT:], [#student-name],
    [EMAIL ADDRESS:], [#student-email],
    [STUDENT’S EMPLOYING ORGANIZATION & LOCATION:], [#location],
    [MENTOR’S NAME:], [#mentor-name],
    [MENTOR’S EMPLOYING ORGANIZATION & LOCATION:], [#mentor-org],
    [MENTOR’S EMAIL ADDRESS:], [#mentor-email],
    [CAPSTONE PROJECT TITLE:], [#title],
  )
 
  #v(1cm)
  #strong("Broad Academic Area of Work:") Web development
 
  #v(0.5cm)
  #strong("Key words:") AWS, CRDT, Distributed, Firebase, JavaScript, Multimedia, Synchronization, Vue.js, WebRTC, WebSocket, Yjs
 
  #v(3cm)
 
  #grid(
    columns: (1fr, 1fr),
    gutter: 20pt,
    align(center)[
        #rect(width: 4cm, height: 2cm, stroke: 1pt)[*Student Sig*]
        #signature-line(width: 150pt) \
        Signature of the Student \
        Name: #student-name \
        Date: #comp-date \
        Place: Nagpur
    ],
    align(center)[
        #rect(width: 4cm, height: 2cm, stroke: 1pt)[*Mentor Sig*]
        #signature-line(width: 150pt) \
        Signature of the Mentor \
        Name: #mentor-name \
        Date: #comp-date \
        Place: Canada
    ]
  )
]

// ── 5. EVALUATION SHEET ───────────────────────────────────────────────
#let evaluation-sheet(title, student-name, student-id, student-email, location, mentor-name, mentor-org, mentor-email) = page[
  #align(center)[
    #text(weight: "bold")[BIRLA INSTITUTE OF TECHNOLOGY & SCIENCE, PILANI] \
    #text(weight: "bold")[WORK-INTEGRATED LEARNING PROGRAMMES DIVISION] \
   
    #v(0.5cm)
    BITS ZC499T Capstone Project EC-3 Pre-Final Evaluation Sheet
  ]
 
  #v(0.5cm)
 
  #table(
    columns: (40%, 60%),
    stroke: none,
    [ID No.:], [#student-id],
    [NAME OF THE STUDENT:], [#student-name],
    [EMAIL ADDRESS:], [#student-email],
    [STUDENT’S EMPLOYING ORGANIZATION & LOCATION:], [#location],
    [MENTOR’S NAME:], [#mentor-name],
    [MENTOR’S EMPLOYING ORGANIZATION & LOCATION:], [#mentor-org],
    [MENTOR’S EMAIL ADDRESS:], [#mentor-email],
    [CAPSTONE PROJECT TITLE:], [#title],
  )
 
  #v(0.5cm)
  #strong("Capstone Project Final Evaluation") (Please put a tick mark in the appropriate box)
 
  #v(0.5cm)
 
  #table(
    columns: (auto, 1fr, 1fr, 1fr, 1fr, 1fr),
    align: (center + horizon),
    [S No.], [Evaluation Component], [Excellent], [Good], [Fair], [Poor],
    [1.], [Final Capstone Project Report], [], [], [], [],
    [2.], [Final Seminar and Viva-Voce], [], [], [], [],
  )
 
  #v(0.5cm)
 
  #table(
    columns: (auto, 3fr, 1fr, 1fr, 1fr, 1fr),
    align: (center + horizon),
    [S.No.], [Evaluation Criteria], [Excellent], [Good], [Fair], [Poor],
    [1], [Technical/Professional Competence], [], [], [], [],
    [2], [Work Progress and Achievements], [], [], [], [],
    [3], [Documentation and expression], [], [], [], [],
    [4], [Initiative and Originality], [], [], [], [],
    [5], [Research & Innovation], [], [], [], [],
    [6], [Relevance to the work environment], [], [], [], [],
    table.cell(colspan: 6, align: left)[
      Please ENCIRCLE the Recommended Final Grade: Excellent / Good / Fair / Poor
    ]
  )
 
  #v(0.5cm)
  #strong("Remarks of the Mentor:")
  #v(1cm)
 
  #table(
    columns: (auto, 1fr, 1fr),
    align: left + horizon,
    [], [#strong("Mentor")], [#strong("Additional Examiner")],
    [Name], [#mentor-name], [Chitra Kumari],
    [Qualification], [MTech], [MCA],
    [Designation], [Project Manager], [Project Lead],
    [Org & Location], [#mentor-org], [HCLTech, Noida],
    [Phone Number], [+91 9742068886], [+91 8130310974],
    [Email Address], [#mentor-email], [chitra.kumari\@hcltech.com],
    [Signature], [
      #rect(width: 3cm, height: 1cm, stroke: 1pt)[*Sig*]
    ], [
      #rect(width: 3cm, height: 1cm, stroke: 1pt)[*Sig*]
    ],
    [Place & Date], [Canada, 26/01/2026], [Noida, 26/01/2026],
  )
]

// ── 6. CONTENTS PLACEHOLDER ───────────────────────────────────────────
#let contents-placeholder() = page[
  #align(center)[#text(size: 14pt, weight: "bold")[TABLE OF CONTENTS]]
   
  1. Introduction \
  2. Problem statement \
  3. Objective of the project \
  4. Background of previous work done (Literature Review) \
  5. Potential challenges & risks \
  6. Major functional and non-functional requirements \
  7. Resources needed \
  8. Detailed Plan of Work done \
  9. Future Work & Scope of improvements \
  Inferences/Summary \
  Conclusions and Recommendations \
  Bibliography \
  Appendices
]

// ── 7. ACKNOWLEDGEMENTS ───────────────────────────────────────────────
#let acknowledgements() = page[
  #align(center)[ #underline[#text(size: 14pt, weight: "bold")[ACKNOWLEDGEMENTS]]]
  #v(1cm)
 
  I would like to express my sincere gratitude to #strong("Ms. Harpreet Kaur"), Project Manager, for her invaluable mentorship and insightful guidance. Her expertise in system architecture and constant encouragement played a pivotal role in shaping this application.
 
  I am also deeply thankful to #strong("Ms. Chitra Kumari"), Project Lead and Additional Examiner, for her technical oversight and constructive feedback, which greatly refined the project's logic and real-time synchronization capabilities.
 
  Furthermore, I extend my appreciation to #strong("Mr. A M Prasad"), Evaluator, for his professional assessment and time. His critical evaluation ensured the project met high technical standards.
 
  Finally, I thank my peers, family, and the open-source communities—particularly the creators of Vue.js, Yjs, and Firebase—for providing the tools and support necessary to complete this distributed collaboration project.
]

// ── 8. CHECKLIST ──────────────────────────────────────────────────────
#let checklist() = page[
  #align(center)[
    #text(weight: "bold")[Checklist of items for the Final Project Report]
  ]
  #text(size: 10pt)[
    This checklist is to be attached as the last page of the report. \
    This checklist is to be duly completed, verified and signed by the student.
  ]
 
  #v(0.5cm)
 
  #table(
    columns: (auto, 1fr, auto),
    align: (center + horizon, left + horizon, center + horizon),
    table.header([*S.No*], [*Item*], [*Yes/No*]),
   
    [1], [Is the final report neatly formatted with all the elements required for a technical Report?], [Yes],
    [2], [Is the Cover page in proper format as given in Annexure A?], [Yes],
    [3], [Is the Title page (Inner cover page) in proper format?], [Yes],
    [4], [ (a) Is the Certificate from the Mentor in proper format? \ (b) Has it been signed by the Mentor?], [Yes \ Yes],
    [5], [Is the Abstract included in the report properly written within one page? Have the technical keywords been specified properly?], [Yes \ Yes],
    [6], [Is the title of your report appropriate? The title should be adequately descriptive, precise and must reflect scope of the actual work done. Uncommon abbreviations / Acronyms should not be used in the title], [Yes],
    [7], [Have you included the List of abbreviations / Acronyms?], [Yes],
    [8], [Does the Report contain a summary of the literature survey?], [Yes],
    [9], [Does the Table of Contents include page numbers? \ Are the Pages numbered properly? \ Are the Figures numbered properly? \ Are the Tables numbered properly? \ Are the Captions for the Figures and Tables proper? \ Are the Appendices numbered properly?], [Yes \ Yes \ Yes \ Yes \ Yes \ Yes],
    [10], [Is the conclusion of the Report based on discussion of the work?], [Yes],
    [11], [Are References or Bibliography given at the end of the Report? \ Have the References been cited properly inside the text of the Report? \ Are all the references cited in the body of the report?], [Yes \ Yes \ Yes],
    [12], [Is the report format and content according to the guidelines? The report should not be a mere printout of a Power Point Presentation, or a user manual. Source code of software need not be included in the report.], [Yes],
  )
 
  #v(1cm)
  #strong("Declaration by Student:") \
  I certify that I have properly verified all the items in this checklist and ensure that the report is in proper format as specified in the course handout.
 
  #v(1cm)
 
  #grid(
    columns: (1fr, 1fr),
    align: (left, right),
    [
        Place: ___Nagpur___ \
        Date: ___26/01/2026___
    ],
    [
        #rect(width: 4cm, height: 1.5cm, stroke: 1pt)[*Student Sig*]
        #signature-line(width: 150pt) \
        Signature of the Student
    ]
  )
 
  #v(0.5cm)
  ID No.: __202117B3596__ \
  Name: ___ANAVADYA S___
]